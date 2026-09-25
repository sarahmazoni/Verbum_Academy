# Verbum Academy

## Plataforma de Aprendizagem de Idiomas

O **Verbum** é uma plataforma web de aprendizagem de idiomas baseada em vocabulário de alta frequência, gramática, expressões frequentes e acompanhamento individual do progresso do estudante.

## Objetivo

O projeto tem como objetivo disponibilizar uma plataforma que organize o aprendizado de idiomas de forma estruturada, permitindo que o usuário acompanhe seu desenvolvimento em diferentes áreas do idioma estudado.

## Funcionalidades

Implementadas nesta entrega:

- Cadastro e autenticação de usuários
- Autenticação em dois fatores (2FA)
- Recuperação de senha por token temporário (expiração 15 min, uso único e logs)

## Stack Tecnológico

### Backend

- Python
- Django

### Banco de Dados

- SQLite

### Frontend

- HTML
- CSS
- JavaScript

### Arquitetura

O sistema utiliza a arquitetura MVT (Model-View-Template) disponibilizada pelo framework Django.

## Segurança

Implementados nesta entrega:

- Hash e salt das senhas (Django)
- 2FA (TOTP)
- Controle e expiração de sessões
- Proteção contra tentativas excessivas de autenticação
- Recuperação de senha por token HMAC temporário
- Logs de solicitação, sucesso e falha da recuperação (sem senha/token)

## Privacidade e LGPD

Implementado nesta entrega (Lei nº 13.709/2018, itens 4.1 a 4.11):

- Inventário de dados pessoais com finalidade e base legal
- Minimização (cadastro sem CPF, telefone ou dado sensível)
- Consentimento explícito, com finalidade, data e versão da política
- Revogação do consentimento
- Consulta dos dados do titular
- Exportação em JSON
- Exclusão da conta e dos dados pessoais

Documentação: `docs/lgpd.md`  
Política versionada: `docs/politica-privacidade.md`

## Como executar

### Ambiente publicado (o que o professor testa)

https://verbum-academy.onrender.com/

### Ambiente local

No PowerShell, na pasta que contém `manage.py`:

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
