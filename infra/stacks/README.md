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
│  │ - S3 Gateway Endpoint (Lambda → S3)                  │   │
│  │ - SSM Interface Endpoints (Session Manager)          │   │
│  │   * SSM, SSM_MESSAGES, EC2_MESSAGES                  │   │
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
│  │ - VPC: Public Subnet (개발 환경)                       │   │
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
- **VPC Endpoints**:
  - S3 Gateway Endpoint (Lambda → S3)
  - SSM Interface Endpoints (Session Manager: SSM, SSM_MESSAGES, EC2_MESSAGES)

### 2️⃣ MyFridger-Recipe (레시피 동기화)

**리소스:**
- **Lambda Function**: Python 3.12, 1024MB, 15분 타임아웃
  - **네트워크**: Public Subnet (개발 환경 - 외부 API 접근)
  - **프로덕션**: Private Subnet + NAT Gateway 권장
- **EventBridge Rule**: 매주 월요일 02:00 KST 실행
- **Lambda Security Group**: VPC 내부 RDS/S3 접근 + 외부 API 접근

**의존성**: FridgerBackend의 VPC, RDS, S3, Secrets 사용

---

## 네트워크 구조

```
VPC: 10.0.0.0/16
├── AZ-A (ap-northeast-2a)
│   ├── Public Subnet (10.0.0.0/24)
│   │   ├── EC2 (Materials API) ← EIP 52.78.138.82
│   │   ├── Lambda (Recipe Sync) ← 개발 환경
│   │   └── SSM Interface Endpoints (Session Manager)
│   └── Private Isolated (10.0.2.0/24)
│       └── RDS PostgreSQL
└── AZ-B (ap-northeast-2b)
    ├── Public Subnet (10.0.1.0/24)
    │   └── (Lambda Multi-AZ 대비)
    └── Private Isolated (10.0.3.0/24)
        └── RDS (Multi-AZ 대비)
```

**라우팅:**
- **Public Subnet** → Internet Gateway (외부 인터넷 양방향 접근)
  - EC2, Lambda가 외부 API 호출 가능
  - EIP를 통해 외부에서 EC2 접근 가능
- **Private Isolated Subnet** → NAT Gateway 없음 (VPC 내부만)
  - RDS는 VPC 내부에서만 접근 가능 (보안)
  - S3 Gateway Endpoint를 통한 S3 접근만 허용

**Internet Gateway 동작:**
```
Lambda (Public Subnet)
    ↕ Route: 0.0.0.0/0 → Internet Gateway
Internet Gateway
    ↕
외부 API (식품안전나라 openapi.foodsafetykorea.go.kr)
```

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
Egress: All  # RDS, S3, Secrets Manager, 외부 API 접근
```

---

## 데이터 흐름

### Materials API 요청:
```
Client → EIP (52.78.138.82) → EC2 (FastAPI) → RDS → Response
```

### Recipe Sync (개발 환경):
```
EventBridge (매주 월요일 02:00 KST)
    ↓
Lambda Function (Public Subnet)
    ├→ Internet Gateway → 식품안전나라 API (레시피 데이터)
    ├→ Secrets Manager (API Key, DB 자격증명)
    ├→ VPC 내부 → RDS (레시피 저장)
    └→ S3 Gateway Endpoint → S3 (이미지 업로드)
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

### Session Manager
- **EC2 IAM Role**: AmazonSSMManagedInstanceCore
- **VPC Interface Endpoints**: SSM, SSM_MESSAGES, EC2_MESSAGES
- **접속 방법**: AWS Console 또는 AWS CLI

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
| Secrets Manager | ~$1.20/월 (3개 secrets × $0.40) |
| VPC Gateway Endpoint (S3) | 무료 |
| VPC Interface Endpoint (SSM) | ~$7.20/월 ($0.01/시간 × 3개 × 720시간) |

**총 예상 비용**: ~$8-10/월 (프리티어 적용 시)

---

## 환경별 네트워크 설정

### 개발 환경 (현재 설정)
```python
# recipe_stack.py:132
vpc_subnets=ec2.SubnetSelection(
    subnet_type=ec2.SubnetType.PUBLIC
)
```

**특징**:
- ✅ Lambda가 외부 API 접근 가능 (Internet Gateway 사용)
- ✅ NAT Gateway 불필요 (비용 절감: ~$45/월)
- ⚠️ Lambda가 Public Subnet에 배치 (보안 저하)
- **용도**: 개발/테스트 환경

### 프로덕션 환경 (권장)
```python
# backend.py:78
nat_gateways=1,  # 0 → 1로 변경

# backend.py:84-86
ec2.SubnetConfiguration(
    name="Private",
    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
    cidr_mask=24,
),

# recipe_stack.py:132
vpc_subnets=ec2.SubnetSelection(
    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
)
```

**특징**:
- ✅ Lambda가 Private Subnet에 배치 (보안 강화)
- ✅ NAT Gateway를 통한 외부 API 접근
- ❌ 추가 비용: ~$45/월 (NAT Gateway)
- **용도**: 프로덕션 환경

---

## 주요 파일

```
infra/
├── app.py                    # 스택 정의 및 연결
├── utils.py                  # Config (EIP, Lambda 설정)
├── cdk.json                  # CDK 설정
└── stacks/
    ├── __init__.py
    ├── backend.py            # 공유 인프라 (VPC, RDS, EC2, S3, SSM)
    └── recipe_stack.py       # Recipe Lambda + EventBridge
```

---

## 문서 정보

- **작성일**: 2025-12-01
- **배포 리전**: ap-northeast-2 (서울)
- **AWS 계정**: 870678672312 (프리티어)
- **CDK 버전**: 2.227.0+
- **환경**: 개발/테스트 (Lambda Public Subnet)
