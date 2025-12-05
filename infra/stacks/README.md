MyFridger Backend - AWS Architecture Diagram
═══════════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  Internet Users                                      │
│                            (Mobile App / Web Clients)                                │
└─────────────────────────┬────────────────────────────┬──────────────────────────────┘
                          │                            │
                          │ HTTPS                      │ HTTPS (Direct Access)
                          ▼                            ▼
              ┌───────────────────────┐    ┌─────────────────────────────┐
              │   Elastic IP (EIP)    │    │      S3 Bucket (Public)     │
              │   52.78.138.82        │    │  myfridger-uploads-*        │
              └───────────┬───────────┘    │  ┌─────────────────────┐   │
                          │                │  │ recipes/{id}/       │   │
                          │                │  │ - thumbnail.jpg     │   │
═════════════════════════▼════════════════│══│ - manual_01.jpg     │═══│═══════════════
║                      VPC (10.0.0.0/16)  │  │ ACL: public-read    │   │              ║
║                                         │  │ Cache: 31536000s    │   │              ║
║  ┌──────────────────────────────────┐  │  └─────────────────────┘   │              ║
║  │  Public Subnet (10.0.0.0/24)     │  │                             │              ║
║  │                                  │  └─────────────────────────────┘              ║
║  │  ┌────────────────────────────┐ │                                                ║
║  │  │   EC2 Instance (Backend)   │ │                                                ║
║  │  │   - Type: t3.micro         │ │                                                ║
║  │  │   - OS: Amazon Linux 2023  │ │                                                ║
║  │  │   - App: FastAPI + Uvicorn │ │                                                ║
║  │  │   - Port: 80 (HTTP)        │ │                                                ║
║  │  │   - IAM: Bedrock Full      │◄┼──────────┐                                     ║
║  │  │   - Env: DATABASE_PASSWORD │ │          │                                     ║
║  │  │          OCR_API_KEY        │ │          │                                     ║
║  │  └───────────┬────────────────┘ │          │                                     ║
║  │              │                   │          │                                     ║
║  │              │ Session Manager   │          │                                     ║
║  │              │ (Browser-based)   │          │                                     ║
║  │              ▼                   │          │ Read Secret                         ║
║  │  ┌────────────────────────────┐ │          │                                     ║
║  │  │  VPC Interface Endpoints   │ │          │                                     ║
║  │  │  - SSM (~$2.40/mo)        │ │          │                                     ║
║  │  │  - SSM Messages            │ │          │                                     ║
║  │  │  - EC2 Messages            │ │          │                                     ║
║  │  └────────────────────────────┘ │          │                                     ║
║  │                                  │          │                                     ║
║  │  ┌────────────────────────────┐ │          │                                     ║
║  │  │   NAT Gateway              │ │          │                                     ║
║  │  │   3.35.124.234             │─┼──────┐   │                                     ║
║  │  │   (~$40/mo)                │ │      │   │                                     ║
║  │  └────────────────────────────┘ │      │   │                                     ║
║  └──────────────────────────────────┘      │   │                                     ║
║                                            │   │                                     ║
║  ┌──────────────────────────────────┐      │   │                                     ║
║  │ Private Subnet (EGRESS)          │      │   │                                     ║
║  │ 10.0.1.0/24                      │      │   │                                     ║
║  │                                  │      │   │                                     ║
║  │  ┌────────────────────────────┐ │      │   │                                     ║
║  │  │ Lambda: RecipeSyncLambda   │ │      │   │                                     ║
║  │  │ - Runtime: Python 3.12     │ │      │   │                                     ║
║  │  │ - Memory: 512 MB           │ │      │   │                                     ║
║  │  │ - Timeout: 600s (10 min)   │ │      │   │                                     ║
║  │  │ - Trigger: EventBridge     │ │      │   │                                     ║
║  │  │   (Monthly, 04:00 KST)     │ │      │   │                                     ║
║  │  │ - Layer: dependencies.zip  │ │      │   │                                     ║
║  │  └───────┬────────────────────┘ │      │   │                                     ║
║  │          │                       │      │   │                                     ║
║  │          │ NAT Gateway           │      │   │                                     ║
║  │          └───────────────────────┼──────┘   │                                     ║
║  │                                  │          │                                     ║
║  └──────────────────────────────────┘          │                                     ║
║                                                │                                     ║
║              │                                 │                                     ║
║              │ 5432 (PostgreSQL)               │                                     ║
║              ▼                                 │                                     ║
║  ┌──────────────────────────────────┐          │                                     ║
║  │ Private Subnet (ISOLATED)        │          │                                     ║
║  │ 10.0.2.0/24                      │          │                                     ║
║  │                                  │          │                                     ║
║  │  ┌────────────────────────────┐ │          │                                     ║
║  │  │  RDS PostgreSQL Instance   │ │          │                                     ║
║  │  │  - Type: db.t3.micro       │ │          │                                     ║
║  │  │  - Engine: PostgreSQL 16   │ │          │                                     ║
║  │  │  - Storage: 20GB GP3       │ │          │                                     ║
║  │  │  - Database: fridger       │ │          │                                     ║
║  │  │  - User: fridger           │ │          │                                     ║
║  │  │  - Multi-AZ: No            │ │          │                                     ║
║  │  │  - Backup: 0 days          │ │          │                                     ║
║  │  │  - Tables:                 │ │          │                                     ║
║  │  │    * materials             │ │          │                                     ║
║  │  │    * recipes               │ │          │                                     ║
║  │  │    * recipe_recommendation │ │          │                                     ║
║  │  └────────────────────────────┘ │          │                                     ║
║  └──────────────────────────────────┘          │                                     ║
║                                                │                                     ║
║  ┌──────────────────────────────────┐          │                                     ║
║  │  VPC Gateway Endpoint (S3)       │          │                                     ║
║  │  - Type: Gateway (Free)          │──────────┼───────┐                             ║
║  │  - Target: Private Subnet        │          │       │                             ║
║  └──────────────────────────────────┘          │       │                             ║
║                                                │       │                             ║
═════════════════════════════════════════════════╪═══════╪═════════════════════════════
                                                 │       │
                         ┌───────────────────────┘       │
                         │                               │
                         ▼                               ▼
┌─────────────────────────────────────┐   ┌──────────────────────────────────────┐
│   AWS Secrets Manager               │   │   Amazon S3                          │
│                                     │   │   myfridger-uploads-870678672312-... │
│  1. fridger/db-credentials          │   │                                      │
│     - username: fridger             │   │   Lambda Upload (via VPC Endpoint):  │
│     - password: auto-generated      │   │   - Timeout: 120s                    │
│                                     │   │   - Follow Redirects: True           │
│  2. fridger/food-safety-api-key     │   │   - ACL: public-read                 │
│     - api_key: YOUR_API_KEY_HERE    │   │   - Content-Type: image/jpeg         │
│                                     │   │   - Cache-Control: max-age=31536000  │
│  3. fridger/recipe-sync-metadata    │   │                                      │
│     - last_sync_date: 20000101      │   │   Objects:                           │
│       (Lambda updates monthly)      │   │   - recipes/1/thumbnail.jpg          │
└─────────────────────────────────────┘   │   - recipes/1/manual_01.jpg          │
                                          │   - ... (1,146 recipes total)        │
         ▲                                └──────────────────────────────────────┘
         │
         │ Read Secret
         │
┌────────┴──────────────────────────────┐
│   Amazon EventBridge                  │
│                                       │
│   Rule: RecipeSyncSchedule            │
│   - Schedule: cron(0 19 1 * ? *)      │
│   - Time: Monthly, 1st day, 04:00 KST │
│   - Target: RecipeSyncLambda          │
│   - Status: Enabled                   │
└───────────────────────────────────────┘


         ▲
         │
         │ Invoke Model
         │
┌────────┴──────────────────────────────┐
│   Amazon Bedrock (us-east-1)          │
│                                       │
│   Model: Nova Lite                    │
│   - Use Case: AI Expiry Estimation    │
│   - API: /recommends/expire           │
│   - Option: use_ai=true (default)     │
│   - Fallback: Rule-based estimation   │
│   - Confidence: 0.8~0.95              │
└───────────────────────────────────────┘


                         External APIs
┌─────────────────────────────────────────────────────────────────┐
│  식품안전나라 (Food Safety Korea) API                            │
│                                                                 │
│  Lambda → NAT Gateway (3.35.124.234) → Internet → API Server    │
│                                                                 │
│  - Endpoint: http://openapi.foodsafetykorea.go.kr/api/...      │
│  - Purpose: Recipe data synchronization                        │
│  - Frequency: Monthly (EventBridge trigger)                    │
│  - Data: Recipe info, ingredients, cooking steps, images       │
└─────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════════
                                   Data Flows
═══════════════════════════════════════════════════════════════════════════════════════

1. User API Request Flow:
   Internet → EIP (52.78.138.82) → EC2 (FastAPI) → RDS (PostgreSQL)
                                 ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←

2. Recipe Sync Flow (Monthly):
   EventBridge → Lambda (Private Subnet) → NAT Gateway → Food Safety API
                    │                          │
                    │                          └─→ S3 (Upload Images via VPC Endpoint)
                    └──────────────────────────→ RDS (Save Recipe Data)
                    └──────────────────────────→ Secrets Manager (Update last_sync_date)

3. Image Access Flow:
   Internet User → S3 (Direct Public Access, No EC2 Proxy)
                   └─→ CloudFront CDN (Optional, future enhancement)

4. AI Expiry Estimation Flow:
   User → EC2 API (/recommends/expire) → Bedrock (us-east-1) → EC2 → User
                                          (Nova Lite Model)

5. Session Manager Access:
   Admin Browser → AWS Console → SSM Interface Endpoints → EC2 Instance
                   (No SSH key required, No port 22 exposure)

6. Recipe Recommendation Flow:
   User → EC2 (/recommends/recipes) → RDS (Query Materials + Recipes)
                                    → Calculate Matching Score:
                                      * Substring matching: "두부" matches "순두부 70g"
                                      * Priority weight: HIGH (D-3) = 2.0x
                                      * Base match ratio × priority weight
                                    ← Return top N recommendations


═══════════════════════════════════════════════════════════════════════════════════════
                              Security Configuration
═══════════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ EC2 Security Group                                                                   │
│ - Ingress: 0.0.0.0/0:22 (SSH), 0.0.0.0/0:80 (HTTP), 0.0.0.0/0:443 (HTTPS)          │
│ - Egress: All traffic allowed                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ RDS Security Group                                                                   │
│ - Ingress: EC2 Security Group:5432, Lambda Security Group:5432                      │
│ - Egress: None (isolated)                                                           │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Lambda Security Group                                                                │
│ - Ingress: None                                                                      │
│ - Egress: All traffic (via NAT Gateway)                                             │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ S3 Bucket Policy (Public Read)                                                       │
│ - public_read_access: True                                                           │
│ - Block Public ACLs: False                                                           │
│ - Block Public Policy: False                                                         │
│ - Ignore Public ACLs: False                                                          │
│ - Restrict Public Buckets: False                                                     │
│ - Object ACL: public-read (set on each upload)                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════════
                              Cost Breakdown (Monthly)
═══════════════════════════════════════════════════════════════════════════════════════

EC2 (t3.micro, on-demand):              ~$7.50
RDS (db.t3.micro):                      ~$15.00
NAT Gateway:                            ~$32.00 (idle) + data transfer
  - Data Processing: $0.045/GB
  - Estimated transfer: ~5GB/month      ~$0.23
S3 Storage (20GB):                      ~$0.50
S3 Requests (PUT/GET):                  ~$0.10
VPC Interface Endpoints (3):            ~$7.20
  - SSM, SSM Messages, EC2 Messages
  - $0.01/hour × 3 endpoints × 720 hours
Elastic IP:                             Free (attached)
VPC Gateway Endpoint (S3):              Free
EventBridge:                            Free (low volume)
Secrets Manager (3 secrets):            ~$1.20
  - $0.40/secret/month
Lambda Execution:                       Free tier eligible
  - 1 invocation/month, 600s × 512MB
Bedrock (Nova Lite):                    Pay per use
  - Input: $0.00006/1K tokens
  - Output: $0.00024/1K tokens
  - Estimated: ~$2-5/month

─────────────────────────────────────────────────────────────────────────────────────
Total Estimated Cost:                   ~$65-70/month
─────────────────────────────────────────────────────────────────────────────────────

Cost Optimization Notes:
- NAT Gateway is the most expensive component (~50% of total)
- Alternative: VPC Endpoints for specific services (more cost-effective if <5GB/month)
- RDS can be stopped when not in use (development only)
- Consider Reserved Instances for 40-60% savings (production)


═══════════════════════════════════════════════════════════════════════════════════════
                           Key Configuration Settings
═══════════════════════════════════════════════════════════════════════════════════════

Environment Variables (EC2):
  - ENVIRONMENT: production
  - DATABASE_HOST: <rds-endpoint>.ap-northeast-2.rds.amazonaws.com
  - DATABASE_PORT: 5432
  - DATABASE_NAME: fridger
  - DATABASE_USER: fridger
  - DATABASE_PASSWORD: <from-secrets-manager>
  - DB_SECRET_NAME: <secret-arn>
  - AWS_REGION: ap-northeast-2
  - OCR_API_KEY: <user-provided>

Environment Variables (Lambda):
  - DATABASE_PASSWORD: Optional (defaults to Secrets Manager)
  - All other settings inherited from backend stack

Recipe Matching Logic:
  - Substring Matching: "두부" matches "순두부 70g" (one-way)
  - Priority Weights:
    * HIGH (D-3): 2.0x multiplier
    * MEDIUM (D-7): 1.3x multiplier
    * NORMAL: 1.0x multiplier
  - Min Match Ratio: 0.3 (default, 30% ingredients must match)
  - Scoring: base_match_ratio × priority_weight

S3 Upload Configuration:
  - Timeout: 120 seconds (increased from 30s)
  - Follow Redirects: True
  - Cache Control: max-age=31536000 (1 year)
  - ACL: public-read (all uploaded objects)
  - Content-Type: Auto-detected (image/jpeg, image/png, image/gif)

Bedrock Configuration:
  - Region: us-east-1 (Nova Lite availability)
  - Model: amazon.nova-lite-v1:0
  - Max Tokens: 2048
  - Temperature: 0.7
  - Fallback: Rule-based estimation if AI fails
