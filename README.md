# Verbum Academy

## Plataforma de Aprendizagem de Idiomas

O **Verbum** é uma plataforma web de aprendizagem de idiomas baseada em vocabulário de alta frequência, gramática, expressões frequentes e acompanhamento individual do progresso do estudante.

## Objetivo

Disponibilizar uma plataforma que organize o aprendizado de idiomas de forma estruturada, com foco em segurança da informação e conformidade com a LGPD (Lei nº 13.709/2018).

## Funcionalidades

- Cadastro e autenticação de usuários
- Autenticação em dois fatores (2FA/TOTP) com segredo cifrado (Fernet)
- Recuperação de senha por token HMAC temporário (15 min, uso único)
- Direitos do titular (consulta, exportação JSON, exclusão e revogação)
- Auditoria de eventos críticos (restrita a staff)
- Proteção contra força bruta (senha e TOTP)

## Stack Tecnológico

### Backend
- Python + Django (arquitetura MVT)

### Banco de Dados
- SQLite

### Frontend
- HTML, CSS e JavaScript

### Segurança
- PBKDF2-HMAC-SHA256 (hash + salt)
- TOTP (pyotp) com segredo Fernet
- Sessão de 30 minutos + cookie HttpOnly
- Rate-limit de tentativas (senha e TOTP)
- Deploy no Render com HTTPS

## Segurança

- Hash e salt de senhas (Django)
- 2FA via TOTP com segredo cifrado
- Sessão de 30 minutos e cookie HttpOnly
- Bloqueio após 5 tentativas (senha e TOTP)
- Recuperação por token HMAC (900 s, uso único)
- Logs sem senha, token ou segredo TOTP
- Painel de auditoria restrito a usuários staff

## Privacidade e LGPD

- Inventário de dados pessoais com finalidade e base legal
- Minimização (sem CPF, telefone ou dados sensíveis)
- Consentimento explícito com data e versão da política
- Consulta, exportação JSON, revogação e exclusão

Documentação: `docs/lgpd.md`  
Política versionada: `docs/politica-privacidade.md`

## Como executar

### Ambiente publicado
https://verbum-academy.onrender.com/

### Ambiente local

```powershell
$env:DJANGO_SECRET_KEY="dev"
$env:VERBUM_ENCRYPTION_KEY="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
$env:DEBUG="True"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Se o pip reclamar do Django 6.1 no Python 3.11:

    python -m pip install dj-database-url cryptography pyotp whitenoise

Acesse: http://127.0.0.1:8000/

As chaves acima são só para desenvolvimento. Em produção elas ficam nas variáveis do Render, não no código.

## Estrutura do Projeto

    Verbum/
    ├── accounts/
    ├── homePage/
    ├── templates/
    ├── docs/
    ├── Verbum/
    ├── manage.py
    ├── requirements.txt
    ├── README.md
    ├── LICENSE
    └── .gitignore

## Documentação

A documentação do Projeto Integrador está em `docs/`.

Etapa atual — Documentação Técnico-Científica (itens 6.1 a 6.12):

- `docs/documentacao-tecnico-cientifica.md`
- `docs/checklist-etapa-documentacao.md`

Documentos reaproveitados nesta etapa:

- `docs/seguranca.md`
- `docs/implementacao.md`
- `docs/recuperacao-senha.md`
- `docs/lgpd.md`
- `docs/testes.md`
- `docs/auditoria-logs.md`
- `docs/evidencias/`

Enunciado e rubrica: `docs/Projeto Integrador.pdf` e `docs/Requisitos(2).pdf`.

## Equipe

- Sarah
- Henrique
- Gabriel

## Entrega Atual

- Aplicação: https://verbum-academy.onrender.com/
- Auditoria (somente leitura): https://verbum-academy.onrender.com/accounts/auditoria/
- Documentação técnico-científica: `docs/documentacao-tecnico-cientifica.md`
- Checklist 6.1–6.12: `docs/checklist-etapa-documentacao.md`
- Kanban: https://github.com/users/sarahmazoni/projects/1
- Release prevista: v1.5.0

## Status

Etapa de Documentação Técnico-Científica em preparação para entrega (prazo 27/09/2026).
