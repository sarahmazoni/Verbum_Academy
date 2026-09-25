# Documentação Técnico-Científica — Verbum Academy

Projeto Integrador — Políticas de Segurança da Informação  
Itens 6.1 a 6.12 da rubrica (item 4.6 do enunciado)

Aplicação: https://verbum-academy.onrender.com/  
Repositório: https://github.com/sarahmazoni/Verbum_Academy  
Equipe: Sarah, Henrique, Gabriel

Fontes: `README.md`, `docs/seguranca.md`, `docs/implementacao.md`, `docs/recuperacao-senha.md`, `docs/lgpd.md`, `docs/testes.md`, `docs/auditoria-logs.md`, `docs/evidencias/`.

---

## 6.1 Documento de visão geral do sistema

O **Verbum** é uma plataforma web de aprendizagem de idiomas baseada em vocabulário de alta frequência, gramática, expressões frequentes e acompanhamento do progresso do estudante.

No escopo desta disciplina, o sistema implementa autenticação e gestão de credenciais, autenticação de dois fatores (2FA TOTP), recuperação de senha por token temporário, criptografia em trânsito e em repouso, conformidade com a LGPD (Lei nº 13.709/2018) e auditoria de eventos críticos.

**Stack:** Python e Django (MVT), SQLite, HTML/CSS/JavaScript. Ambiente de avaliação no Render com HTTPS: https://verbum-academy.onrender.com/

**Módulos:** `accounts/` (cadastro, login, 2FA, reset, privacidade, auditoria), `homePage/`, `templates/`, `docs/`.

---

## 6.2 Diagrama de arquitetura

```mermaid
flowchart LR
  U[Navegador do titular] -->|HTTPS TLS| R[Render]
  R --> D[Django MVT]
  D --> A[accounts]
  D --> H[homePage]
  D --> DB[(SQLite: User, UserProfile, ConsentRecord)]
  D --> L[verbum.log]
  D --> F[Fernet - totp_secret]
