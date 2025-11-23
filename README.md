# MyFridger Backend
> 클라우드 프로젝트 G조

# Getting Started
- 해당 프로젝트는 `uv`를 사용합니다.

## Setup
```bash
uv sync
```

## Dev
```bash
uv run fastapi dev main.py
```

### Migration
- Migration 생성
```bash
alembic revision --autogenerate -m "[MIGRATION_MESSAGE]"
```
- DB에 적용
```bash
alembic upgrade head
```

### Test
```bash
uv run pytest
```

# Environments
```shell
ENV=development # development or production

# DB는 postgresql을 사용합니다.
DATABASE_NAME=name
DATABASE_USER=user
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```
