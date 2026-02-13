# ArcanaWhisper Backend

<p align="center">
  <strong>AI 타로 리딩 서비스 백엔드 API</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/AWS_Lambda-Serverless-FF9900?logo=awslambda&logoColor=white" alt="AWS Lambda">
  <img src="https://img.shields.io/badge/API_Gateway-HTTP_API-FF4F8B?logo=amazonapigateway&logoColor=white" alt="API Gateway">
  <img src="https://img.shields.io/badge/Firebase-Firestore-FFCA28?logo=firebase&logoColor=black" alt="Firebase">
  <img src="https://img.shields.io/badge/Google-Gemini-4285F4?logo=googlegemini&logoColor=white" alt="Gemini">
</p>

<p align="center">
  <a href="https://www.aitarot.site">Service</a> •  
  <a href="https://github.com/gguip1/ArcanaWhisper-Front">Frontend Repo</a>
</p>

---

## 소개

ArcanaWhisper Backend는 AI 타로 리딩 서비스의 API 서버입니다. AWS Lambda 기반 서버리스 아키텍처로 구축되었으며, Google Gemini와 LangChain을 활용하여 타로 해석을 제공합니다.

### 핵심 특징

- **서버리스** - AWS Lambda로 운영 비용 최적화
- **확장성** - API Gateway + Lambda 자동 스케일링
- **보안** - Firebase Auth 토큰 검증, SSM Parameter Store 시크릿 관리

---

## 아키텍처

<!--
  [아키텍처 다이어그램]
  파일: assets/readme/architecture.png (800x500px)

  다이어그램에 포함할 내용:
  1. Client (Browser/Mobile)
  2. API Gateway HTTP API
  3. AWS Lambda (Python 3.11)
  4. External Services:
     - Google Gemini API (AI)
     - Firebase Auth (인증)
     - Firebase Firestore (DB)
  5. AWS SSM Parameter Store (Secrets)

  권장 도구: draw.io, Excalidraw, Lucidchart
  스타일: 다크 테마, 미니멀, 화살표로 데이터 흐름 표시
-->

<img width="2182" height="1224" alt="image" src="https://github.com/user-attachments/assets/e8886712-90f8-4e5b-a6b9-c3c3fa95eb2f" />

---

## 기술 스택

### Backend

| Category | Technology                |
| -------- | ------------------------- |
| Language | Python 3.11               |
| Compute  | AWS Lambda (Serverless)   |
| API      | API Gateway HTTP API      |
| AI/LLM   | LangChain + Google Gemini |
| Database | Firebase Firestore        |
| Auth     | Firebase Authentication   |
| Secrets  | AWS SSM Parameter Store   |
| IaC      | AWS SAM                   |

### DevOps

| Category   | Technology      |
| ---------- | --------------- |
| CI/CD      | GitHub Actions  |
| Deployment | AWS SAM CLI     |
| Monitoring | CloudWatch Logs |

---

## 주요 기능

| 기능          | 설명                                      |
| ------------- | ----------------------------------------- |
| AI 타로 리딩  | Gemini 기반 타로 해석                     |
| 사용자 인증   | Firebase ID Token 검증 (Google, Apple)    |
| Rate Limiting | Guest 1회/일, 로그인 사용자 10회/일       |
| 히스토리      | 로그인 사용자 타로 기록 저장 및 조회      |
| 사용량 조회   | 일일 사용량 및 리셋 시간 확인             |
| 결과 공유     | 카카오톡 등 외부 공유 링크 생성 (30일 만료) |

---

## API 엔드포인트

| Method | Endpoint              | Description      | Auth       |
| ------ | --------------------- | ---------------- | ---------- |
| `GET`  | `/health`             | 헬스 체크        | -          |
| `POST` | `/tarot`              | 타로 리딩 요청   | Required   |
| `GET`  | `/usage`              | 사용량 조회      | Required   |
| `GET`  | `/tarot/history`      | 히스토리 조회    | Login Only |
| `POST` | `/readings`           | 공유 링크 생성   | Required   |
| `GET`  | `/readings/{share_id}`| 공유 결과 조회   | -          |

### 인증 방식

```bash
# 로그인 사용자
Authorization: Bearer <firebase_id_token>

# Guest (비로그인)
X-Guest-Token: <uuid>
```

### Rate Limit

| 사용자 | 일일 제한 | 리셋 시간 |
| ------ | --------- | --------- |
| Guest  | 1회       | KST 00:00 |
| 로그인 | 10회      | KST 00:00 |

<!-- > 상세 API 문서: [docs/api-reference.md](./docs/api-reference.md) -->

---

## 프로젝트 구조

```
├── src/
│   ├── lambda_handler.py        # Lambda 엔트리포인트, 라우팅
│   ├── services/                # 비즈니스 로직
│   │   ├── tarot_service.py     # 타로 리딩 서비스
│   │   ├── history_service.py   # 히스토리 서비스
│   │   └── usage_service.py     # Rate Limit 서비스
│   ├── repository/              # 데이터 접근 계층
│   │   ├── history_repository.py
│   │   └── reading_repository.py # 공유 링크 관리
│   └── schema/                  # Pydantic 모델
│       └── tarot.py
├── infra/
│   └── template.yaml            # AWS SAM 템플릿
├── docs/                        # API 문서
├── .github/workflows/           # CI/CD
└── requirements.txt
```

---

## 시작하기

### 사전 요구사항

- Python 3.11+
- AWS CLI & SAM CLI
- Firebase 프로젝트 (Firestore, Auth 활성화)

### 설치

```bash
# 저장소 클론
git clone https://github.com/gguip1/ArcanaWhisper-Back.git
cd ArcanaWhisper-Back

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 환경 변수 설정

```bash
# SSM Parameter Store에 시크릿 저장 (AWS CLI)
aws ssm put-parameter --name "/arcana-whisper/gemini-api-key" --value "your-api-key" --type SecureString
aws ssm put-parameter --name "/arcana-whisper/firebase-credentials" --value "base64-encoded-json" --type SecureString
```

### 배포

```bash
cd infra
sam build
sam deploy --guided
```

---

## 데이터베이스 구조

### Firestore Collections

```
guest_usage/
  └── {guest_token}/
        ├── count: number
        ├── date: "YYYY-MM-DD"
        └── updated_at: "ISO8601"

user_usage/
  └── {firebase_uid}/
        ├── count: number
        ├── date: "YYYY-MM-DD"
        └── updated_at: "ISO8601"

tarot_history/
  └── {history_id}/
        ├── user_id: string
        ├── provider: string
        ├── question: string
        ├── cards: { cards: number[], reversed: boolean[] }
        ├── result: string
        ├── created_at: timestamp
        └── is_shared: boolean        # 공유 여부

readings/
  └── {share_id}/                     # UUID
        ├── history_id: string        # tarot_history 참조
        ├── created_at: timestamp
        └── expires_at: timestamp     # 30일 후 만료 (TTL)
```

---

## 관련 저장소

| Repository                                                           | Description                   |
| -------------------------------------------------------------------- | ----------------------------- |
| [ArcanaWhisper-Front](https://github.com/gguip1/ArcanaWhisper-Front) | React + TypeScript 프론트엔드 |
