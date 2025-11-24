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
uv run fastapi dev app/main.py
```

### Migration
- Migration 생성
```bash
uv run alembic revision --autogenerate -m "[MIGRATION_MESSAGE]"
```
- DB에 적용
```bash
uv run alembic upgrade head
```

### Test
```bash
uv run pytest
```

### AWS Deployment
 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

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
