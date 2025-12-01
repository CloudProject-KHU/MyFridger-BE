# MyFridger AWS Infrastructure

## 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    FridgerBackend Stack                     │
│  (공유 인프라 - VPC, RDS, EC2, S3, Secrets)                   │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │     VPC     │  │ RDS Postgres │  │   S3 Bucket     │     │
│  │ 10.0.0.0/16 │  │  db.t3.micro │  │ (레시피 이미지)   │     │
│  │  2 AZ, NAT:0│  │    20GB GP3  │  │                 │     │
│  └─────────────┘  └──────────────┘  └─────────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ EC2 Instance (Materials API)                         │   │
│  │ - FastAPI Server (Port 80)                           │   │
│  │ - EIP: 52.78.138.82                                  │   │
│  │ - Public Subnet                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Secrets Manager                                      │   │
│  │ - DB Credentials                                     │   │
│  │ - Food Safety API Key                                │   │
│  │ - Recipe Sync Metadata                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ VPC Endpoints                                        │   │
│  │ - S3 Gateway Endpoint                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               ↓ 의존성
┌─────────────────────────────────────────────────────────────┐
│                   MyFridger-Recipe Stack                    │
│          (레시피 동기화 - Lambda + EventBridge)               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Lambda Function (Recipe Sync)                        │   │
│  │ - Runtime: Python 3.12                               │   │
│  │ - Memory: 1024MB, Timeout: 15min                     │   │
│  │ - VPC: Private Isolated Subnet                       │   │
│  │ - 식품안전나라 API → RDS/S3 저장                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ EventBridge Rule                                     │   │
│  │ - Schedule: 매주 월요일 02:00 KST                      │   │
│  │ - Target: Lambda Function                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

<br>
<br>

---

## 스택 구성

### 1️⃣ FridgerBackend (공유 인프라)

**리소스:**
- **VPC**: 10.0.0.0/16, 2 AZ, NAT Gateway 없음
  - Public Subnet: 10.0.0.0/24, 10.0.1.0/24
  - Private Isolated Subnet: 10.0.2.0/24, 10.0.3.0/24
- **RDS PostgreSQL 16**: db.t3.micro, 20GB GP3 (프리티어)
- **EC2 (Materials API)**: t3.micro, FastAPI, EIP 52.78.138.82
- **S3 Bucket**: 레시피 이미지 저장
- **Secrets Manager**: DB 자격증명, API Keys
- **VPC Endpoints**: S3 (Gateway)

### 2️⃣ MyFridger-Recipe (레시피 동기화)

**리소스:**
- **Lambda Function**: Python 3.12, 1024MB, 15분 타임아웃
- **EventBridge Rule**: 매주 월요일 02:00 KST 실행
- **Lambda Security Group**: VPC 내부 RDS/S3 접근

**의존성**: FridgerBackend의 VPC, RDS, S3, Secrets 사용

---

## 네트워크 구조

```
VPC: 10.0.0.0/16
├── AZ-A (ap-northeast-2a)
│   ├── Public Subnet (10.0.0.0/24)
│   │   └── EC2 (Materials API) ← EIP 52.78.138.82
│   └── Private Isolated (10.0.2.0/24)
│       ├── RDS PostgreSQL
│       └── Lambda (Recipe Sync)
└── AZ-B (ap-northeast-2b)
    ├── Public Subnet (10.0.1.0/24)
    └── Private Isolated (10.0.3.0/24)
        └── RDS (Multi-AZ 대비)
```

**라우팅:**
- Public Subnet → Internet Gateway
- Private Isolated → NAT Gateway 없음 (VPC Endpoint 사용)

---

## Security Groups

```python
# EC2 Security Group
Ingress:
  - 0.0.0.0/0 → TCP 22 (SSH)
  - 0.0.0.0/0 → TCP 80 (HTTP)
  - 0.0.0.0/0 → TCP 443 (HTTPS)
Egress: All

# RDS Security Group
Ingress:
  - EC2 Security Group → TCP 5432
  - 10.0.0.0/16 (VPC CIDR) → TCP 5432  # Lambda 접근
Egress: None

# Lambda Security Group
Ingress: None
Egress: All  # RDS, S3, Secrets Manager 접근
```

---

## 데이터 흐름

### Materials API 요청:
```
Client → EIP (52.78.138.82) → EC2 (FastAPI) → RDS → Response
```

### Recipe Sync:
```
EventBridge (매주 월요일 02:00)
    ↓
Lambda Function
    ├→ Secrets Manager (API Key)
    ├→ 식품안전나라 API (레시피 데이터)
    ├→ RDS (레시피 저장)
    └→ S3 (이미지 업로드)
```

---

## 주요 설정

### Database (RDS)
- **Database Name**: `fridger`
- **Username**: `fridger`
- **Connection**: Private Subnet, VPC 내부 접근만

### S3 Bucket
- **Naming**: `myfridger-uploads-{account}-{region}`
- **CORS**: GET, PUT, POST 허용
- **Encryption**: S3-Managed (SSE-S3)

### Lambda Environment
```env
ENVIRONMENT=production
DATABASE_HOST=<rds-endpoint>
DATABASE_NAME=fridger
S3_BUCKET_NAME=<bucket-name>
FOOD_SAFETY_API_BASE_URL=http://openapi.foodsafetykorea.go.kr/api
```

---

## 배포

### 배포 순서:
```bash
1. cdk deploy FridgerBackend       # 공유 인프라
2. cdk deploy MyFridger-Recipe     # Recipe 스택 (의존성 자동)
```

### 한 번에 배포:
```bash
cdk deploy --all
```

### 배포 후 확인:
```bash
# CloudFormation Outputs 확인
aws cloudformation describe-stacks \
  --stack-name FridgerBackend \
  --query 'Stacks[0].Outputs'

# EC2 접속 (Session Manager)
aws ssm start-session --target <instance-id>

# API 테스트
curl http://52.78.138.82/docs
```

---

## 비용 예상 (프리티어)

| 리소스 | 비용 |
|--------|------|
| EC2 (t3.micro) | 무료 (750시간/월) |
| RDS (db.t3.micro, 20GB) | 무료 (750시간/월, 20GB) |
| S3 | 무료 (5GB, 20K GET, 2K PUT) |
| Lambda | 무료 (100만 requests, 400K GB-초) |
| Secrets Manager | ~$1.20/월 (3개 secrets) |
| VPC Gateway Endpoint (S3) | 무료 |
| VPC Interface Endpoint (SSM) | ~$7.20/월 (0.01$/시간 × 3개) |

**총 예상 비용**: ~$8-10/월 (프리티어 적용 시)

---

## 제한사항

### ❌ Lambda 외부 API 접근 불가
- Private Isolated Subnet + NAT Gateway 없음
- 식품안전나라 API 호출 불가 (해결 필요)

**해결 방안:**
1. NAT Gateway 추가 (~$45/월)
2. Lambda를 Public Subnet에 배치 (보안 저하)
3. VPC Endpoint 추가 (API 지원 시)

---

## 주요 파일

```
infra/
├── app.py                    # 스택 정의 및 연결
├── utils.py                  # Config (EIP, Lambda 설정)
├── cdk.json                  # CDK 설정
└── stacks/
    ├── __init__.py
    ├── backend.py            # 공유 인프라 (VPC, RDS, EC2, S3)
    └── recipe_stack.py       # Recipe Lambda + EventBridge
```

---

## 문서 정보

- **작성일**: 2025-12-01
- **배포 리전**: ap-northeast-2 (서울)
- **AWS 계정**: 870678672312 (프리티어)
- **CDK 버전**: 2.227.0+
