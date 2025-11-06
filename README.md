# django_base

Projeto base Django com uma aplicação `account` pronta para autenticação/usuários e estrutura mínima para iniciar rapidamente um projeto REST com Django + DRF.

## Visão geral

Este repositório contém uma base para aplicações Django modernas:

- Aplicação `account` com modelos, serializadores, serviços e views (API) para gerenciar usuários e autenticação.
- Integração com Django REST Framework (DRF) e suporte a JWT (Simple JWT).
- Configurações mínimas em `settings/` para rodar localmente (ASGI/WGSI prontos).

> Estrutura principal:

```
manage.py
pyproject.toml
account/        # app principal (models, serializers, services, views, tests)
settings/       # configurações do Django (dev/prod se necessário)
```

## Funcionalidades principais

- CRUD básico e endpoints de autenticação para usuários (dentro de `account/views.py`).
- Serializers e serviços para separar lógica de negócios (`account/serializers.py`, `account/services.py`).
- Gerenciamento de URLs de autenticação em `account/auth_urls.py` e roteamento principal em `settings/urls.py`.
- Uso de JWT para autenticação via `djangorestframework-simplejwt`.

## Dependências

As dependências estão listadas em `pyproject.toml`. Principais pacotes:

- Django 5.2.x
- djangorestframework
- djangorestframework-simplejwt
- django-cors-headers
- python-decouple (para variáveis de ambiente)
- pillow (para manipulação de imagens, se necessário)
- requests, google-auth e pacotes auxiliares

Recomenda-se usar um ambiente virtual e instalar as dependências via Poetry (ou pip se preferir) — veja a seção "Como rodar".

## Requisitos

- Python 3.13 (conforme `pyproject.toml`: `>=3.13,<4`)
- PostgreSQL ou outro banco suportado pelo Django (ou SQLite para desenvolvimento)

## Como rodar localmente (modo rápido)

1. Clone o repositório

```bash
git clone <repo-url> django_base
cd django_base
```

2. Crie e ative um ambiente virtual (venv)

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instale dependências

Se você usa Poetry (recomendado, já que existe `pyproject.toml`):

```bash
poetry install
```

Se preferir pip (gera `requirements.txt` manualmente):

```bash
pip install -r requirements.txt  # se você gerar esse arquivo previamente
# OU instalar manualmente as dependências listadas no pyproject.toml
pip install "django==5.2.7" djangorestframework djangorestframework-simplejwt python-decouple django-cors-headers pillow
```

4. Configure variáveis de ambiente

- Crie um arquivo `.env` na raiz (o projeto usa `python-decouple`) com as chaves mínimas, por exemplo:

```
SECRET_KEY=uma_chave_secreta_de_teste
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost
```

Ajuste `DATABASE_URL` para seu banco real se não usar SQLite.

5. Rode migrações

```bash
python manage.py migrate
```

6. Crie um superusuário (opcional)

```bash
python manage.py createsuperuser
```

7. Rode o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse http://127.0.0.1:8000/ e os endpoints de API configurados (ver `settings/urls.py` e `account/auth_urls.py`).

## Execução com Docker (opcional)

Este repositório não inclui um Dockerfile por padrão. Se desejar, você pode criar um Dockerfile simples e `docker-compose.yml` para orquestrar banco + app. Posso adicionar isso se quiser.


## Notas de desenvolvimento

- Seguir separação de responsabilidades: `serializers` para validação/serialização, `services` para lógica de negócio.
- Verificar `account/managers.py` se você customizou o `UserManager`.
- Rotas e nomes dos endpoints podem ser encontrados em `account/urls.py` / `account/auth_urls.py` e referenciadas em `settings/urls.py`.

## Próximos passos

- Criar `Dockerfile` e `docker-compose.yml` para facilitar testes locais.
- Cobertura de testes: adicionar testes para serviços e endpoints críticos.
