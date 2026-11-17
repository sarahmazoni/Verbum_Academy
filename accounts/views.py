from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings
from pathlib import Path
from .models import UserProfile, ConsentRecord
from django.contrib.auth import views as auth_views
from accounts.crypto import encrypt_totp_secret, decrypt_totp_secret
import pyotp
import logging


# Logger do app accounts
logger = logging.getLogger(__name__)

# Máximo de tentativas de senha errada antes do bloqueio temporário
MAX_LOGIN_ATTEMPTS = 5

# Duração do bloqueio após atingir o limite de tentativas
LOCKOUT_DURATION = timedelta(minutes=5)


def _client_ip(request):
    return request.META.get('REMOTE_ADDR', '-')


def audit_log(request, event, success, message, user=None, email=None):
    # Não registra senha, token, código 2FA, secret TOTP ou hash.
    if user is not None:
        user_id = getattr(user, 'id', '-')
        email = email or getattr(user, 'email', '-')
    else:
        user_id = '-'
        email = email or '-'

    logger.info(
        'event=%s success=%s user_id=%s email=%s ip=%s message=%s',
        event,
        str(success).lower(),
        user_id,
        email,
        _client_ip(request),
        message,
    )


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')

        # Verifica se as senhas são iguais
        if password != password_confirmation:
            return render(
                request,
                'register.html',
                {'error': 'As senhas não coincidem.'}
            )

        # Verifica se o usuário já existe
        if User.objects.filter(username=username).exists():
            return render(
                request,
                'register.html',
                {'error': 'Este nome de usuário já está cadastrado.'}
            )

        # Valida a senha
        try:
            validate_password(password)
        except ValidationError as e:
            return render(
                request,
                'register.html',
                {'error': ' '.join(e.messages)}
            )

        # Verifica o aceite da política de privacidade
        if not request.POST.get('consent'):
            return render(
                request,
                'register.html',
                {
                    'error': 'É necessário aceitar a Política de Privacidade para criar a conta.'
                }
            )

        # Cria o usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Cria o perfil com o idioma padrão definido no model
        UserProfile.objects.create(user=user)

        # Registra o consentimento
        ConsentRecord.objects.create(
            user=user,
            purpose=ConsentRecord.PURPOSE_DEFAULT,
            granted=True,
            policy_version="1.0",
            source="register",
        )

        logger.info("Consentimento registrado no cadastro.")

        return render(
            request,
            'register.html',
            {'success': 'Usuário cadastrado com sucesso!'}
        )

    return render(request, 'register.html')


def login_view(request):
    # A tela de login está na home
    if request.method != 'POST':
        return redirect('/')

    email = request.POST.get('email')
    password = request.POST.get('password')

    # Localiza o usuário pelo e-mail
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        user = None

    if user is not None:

        # Busca ou cria o perfil
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Verifica se a conta está bloqueada
        if profile.locked_until is not None:

            if timezone.now() < profile.locked_until:
                audit_log(
                    request,
                    event='ACCOUNT_LOCKED',
                    success=False,
                    message='Conta bloqueada por excesso de tentativas.',
                    user=user,
                    email=user.email,
                )

                messages.error(
                    request,
                    'Conta temporariamente bloqueada. Tente novamente mais tarde.'
                )

                return redirect('/')

            # Libera a conta após o período de bloqueio
            profile.locked_until = None
            profile.failed_login_attempts = 0

            profile.save(
                update_fields=['locked_until', 'failed_login_attempts']
            )

        # Verifica a senha
        authenticated_user = authenticate(
            request,
            username=user.username,
            password=password
        )

        if authenticated_user is not None:

            # Zera as tentativas anteriores
            profile.failed_login_attempts = 0
            profile.locked_until = None

            profile.save(
                update_fields=['failed_login_attempts', 'locked_until']
            )

            # Registra login bem-sucedido
            audit_log(
                request,
                event='LOGIN_SUCCESS',
                success=True,
                message='Autenticação primária concluída com sucesso.',
                user=authenticated_user,
                email=authenticated_user.email,
            )

            # Verifica se o usuário possui 2FA
            if profile.two_factor_enabled:
                request.session['pending_2fa_user_id'] = authenticated_user.id
                return redirect('verify_2fa')

            # Finaliza o login
            auth_login(request, authenticated_user)

            return redirect('painel')

        else:
            # Senha incorreta
            profile.failed_login_attempts += 1

            # Verifica se atingiu o limite de tentativas
            if profile.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:

                profile.locked_until = timezone.now() + LOCKOUT_DURATION

                profile.save(
                    update_fields=['failed_login_attempts', 'locked_until']
                )

                audit_log(
                    request,
                    event='LOGIN_FAILURE',
                    success=False,
                    message='Falha na autenticação primária.',
                    user=user,
                    email=user.email,
                )

                audit_log(
                    request,
                    event='ACCOUNT_LOCKED',
                    success=False,
                    message='Conta bloqueada por excesso de tentativas.',
                    user=user,
                    email=user.email,
                )

                messages.error(
                    request,
                    'Conta temporariamente bloqueada. Tente novamente mais tarde.'
                )

                return redirect('/')

            profile.save(
                update_fields=['failed_login_attempts']
            )

            audit_log(
                request,
                event='LOGIN_FAILURE',
                success=False,
                message='Falha na autenticação primária.',
                user=user,
                email=user.email,
            )

    else:
        # E-mail inexistente
        audit_log(
            request,
            event='LOGIN_FAILURE',
            success=False,
            message='Falha na autenticação primária.',
            email=email or '-',
        )

    messages.error(request, 'Email ou senha inválidos.')

    return redirect('/')

# PERFIL DO USUÁRIO E SELEÇÃO DE IDIOMA

@login_required(login_url="homePage")
def perfil(request):

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        idioma = request.POST.get("study_language", "en")

        # Verifica se o idioma enviado é válido
        if idioma in dict(UserProfile.LANGUAGE_CHOICES):

            # Salva o idioma escolhido no banco de dados
            profile.study_language = idioma

            profile.save(
                update_fields=["study_language"]
            )

            messages.success(
                request,
                "Idioma de estudo atualizado."
            )

            return redirect("perfil")

        messages.error(
            request,
            "Selecione um idioma válido."
        )

    return render(
        request,
        "accounts/user.html",
        {
            "two_factor_enabled": profile.two_factor_enabled,
            "study_language": profile.study_language,
        },
    )

# VALIDAÇÃO DO 2FA

def verify_2fa(request):

    # Recupera o ID armazenado na sessão
    user_id = request.session.get('pending_2fa_user_id')

    if not user_id:
        return redirect('/')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session.pop('pending_2fa_user_id', None)
        return redirect('/')

    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':

        codigo = request.POST.get('codigo', '').strip()

        secret = decrypt_totp_secret(profile.totp_secret)

        totp = pyotp.TOTP(secret)

        if totp.verify(codigo):

            # Login após validar o segundo fator
            auth_login(request, user)

            audit_log(
                request,
                event='2FA_SUCCESS',
                success=True,
                message='Validação de 2FA concluída com sucesso.',
                user=user,
                email=user.email,
            )

            request.session.pop('pending_2fa_user_id', None)

            return redirect('painel')

        audit_log(
            request,
            event='2FA_FAILURE',
            success=False,
            message='Falha na validação de 2FA.',
            user=user,
            email=user.email,
        )

        return render(
            request,
            'verify_2fa.html',
            {'error': 'Código 2FA inválido.'}
        )

    return render(request, 'verify_2fa.html')

# PAINEL DO USUÁRIO

@login_required(login_url="homePage")
def painel(request):

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'painel.html',
        {
            'study_language': profile.study_language,
        },
    )


# CONFIGURAÇÃO DO 2FA


@login_required
def setup_2fa(request):

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user
    )

    # Cria um secret caso ainda não exista
    if not profile.totp_secret:

        secret = pyotp.random_base32()

        profile.totp_secret = encrypt_totp_secret(secret)

        profile.save()

    else:
        secret = decrypt_totp_secret(profile.totp_secret)

    totp = pyotp.TOTP(secret)

    if request.method == 'POST':

        codigo = request.POST.get('codigo', '').strip()

        if totp.verify(codigo):

            profile.two_factor_enabled = True

            profile.save()

            messages.success(
                request,
                'Autenticação em dois fatores ativada com sucesso!'
            )

            return redirect('painel')

        messages.error(
            request,
            'Código inválido. Tente novamente.'
        )

    provisioning_uri = totp.provisioning_uri(
        name=request.user.email,
        issuer_name='Verbum'
    )

    return render(
        request,
        'accounts/setup_2fa.html',
        {
            'secret': secret,
            'provisioning_uri': provisioning_uri,
        }
    )

# LOGOUT

def logout_view(request):

    if request.user.is_authenticated:

        audit_log(
            request,
            event='LOGOUT',
            success=True,
            message='Sessão encerrada pelo usuário.',
            user=request.user,
            email=request.user.email,
        )

    logout(request)

    return redirect('/')

# RECUPERAÇÃO DE SENHA

class PasswordResetRequestView(auth_views.PasswordResetView):

    def form_valid(self, form):

        logger.info(
            'Solicitação de recuperação de senha recebida.'
        )

        return super().form_valid(form)


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        if getattr(response, 'context_data', {}).get('validlink') is False:

            logger.warning(
                'Tentativa de recuperação de senha com token inválido ou expirado.'
            )

        return response

    def form_valid(self, form):

        logger.info(
            'Recuperação de senha concluída com sucesso.'
        )

        return super().form_valid(form)


# POLÍTICA DE PRIVACIDADE

def politica_privacidade(request):

    return render(
        request,
        'accounts/politica_privacidade.html',
        {
            'policy_version': '1.0'
        },
    )


@login_required
def privacidade(request):

    logger.info(
        "Titular consultou os dados pessoais."
    )

    ultimo = request.user.consents.first()

    return render(
        request,
        'accounts/privacidade.html',
        {
            'ultimo_consentimento': ultimo
        },
    )


@login_required
def exportar_dados(request):

    ultimo = request.user.consents.first()

    payload = {
        'username': request.user.username,
        'email': request.user.email,
        'date_joined': request.user.date_joined.isoformat(),

        'consentimento': None if ultimo is None else {
            'finalidade': ultimo.purpose,
            'concedido': ultimo.granted,
            'data': ultimo.granted_at.isoformat(),
            'revogado_em': (
                None if ultimo.revoked_at is None
                else ultimo.revoked_at.isoformat()
            ),
            'versao_politica': ultimo.policy_version,
        },
    }

    logger.info(
        "Titular exportou os dados pessoais."
    )

    response = JsonResponse(
        payload,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 2
        }
    )

    response['Content-Disposition'] = (
        'attachment; filename="meus-dados-verbum.json"'
    )

    return response


@login_required
def revogar_consentimento(request):

    if request.method != 'POST':
        return redirect('privacidade')

    ultimo = request.user.consents.first()

    if ultimo is not None and ultimo.granted:

        ultimo.granted = False
        ultimo.revoked_at = timezone.now()

        ultimo.save(
            update_fields=['granted', 'revoked_at']
        )

        logger.info(
            "Titular revogou o consentimento."
        )

        messages.success(
            request,
            'Consentimento revogado.'
        )

    else:

        ConsentRecord.objects.create(
            user=request.user,
            purpose=ConsentRecord.PURPOSE_DEFAULT,
            granted=True,
            policy_version='1.0',
            source='privacidade',
        )

        logger.info(
            "Titular renovou o consentimento."
        )

        messages.success(
            request,
            'Consentimento renovado (política v1.0).'
        )

    return redirect('privacidade')


@login_required
def excluir_conta(request):

    if request.method != 'POST':
        return redirect('privacidade')

    email = request.POST.get('email', '')
    password = request.POST.get('password', '')

    if email.lower() != request.user.email.lower():

        messages.error(
            request,
            'O e-mail informado não confere.'
        )

        return redirect('privacidade')

    if authenticate(
        request,
        username=request.user.username,
        password=password
    ) is None:

        messages.error(
            request,
            'Senha incorreta. A conta não foi excluída.'
        )

        return redirect('privacidade')

    logger.info(
        "Titular solicitou exclusão da conta."
    )

    user = request.user

    logout(request)

    user.delete()

    return render(
        request,
        'accounts/conta_excluida.html'
    )

# AUDITORIA

@login_required
def auditoria_logs(request):

    log_path = Path(settings.BASE_DIR) / 'verbum.log'

    linhas = []

    if log_path.exists():

        with log_path.open(
            encoding='utf-8',
            errors='replace'
        ) as arquivo:

            linhas = arquivo.read().splitlines()[-200:]

    return render(
        request,
        'accounts/auditoria_logs.html',
        {
            'linhas': linhas
        },
    )