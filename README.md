# STORY / REELS — 이론 기반 인스타 릴스 대본 코치

영상 구조·연출에 대한 이해를 바탕으로 사용자가 자신의 목적에 맞는 릴스 대본을 작성하도록 돕는 FastAPI 웹 챗봇입니다. 처음 영상을 만드는 크리에이터가 주제·시청자·등장인물·연출을 대화로 정리하고, 확인한 조건과 영상·미디어 이론을 참고해 촬영 가능한 대본을 만들도록 돕습니다.

저장소: [bidulgiya999/codyssey_work_B7-1-team-](https://github.com/bidulgiya999/codyssey_work_B7-1-team-) · [현재 구현 브랜치](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/tree/feature/c-ai-deploy)

팀 구성: **A 이송하 — 웹 화면·서비스 기획 / B 김시현 — 인증·DB·대화 기록 / C 황승재 — AI 챗봇·서버 배포**. 역할과 작업 경계는 [팀 문서](docs/TEAM.md), 서비스 범위는 [기획 문서](docs/PROJECT.md)를 따른다.

## 핵심 시나리오

1. 회원가입·로그인 후 새 릴스 기획을 시작합니다.
2. 아이디어를 자유롭게 말하면 이미 답한 조건은 보존하고 부족한 내용을 한 번에 1~2개 묻습니다.
3. 주제·목적·타겟 세그먼트·연령·길이·등장 방식·연출·핵심 메시지를 요약합니다.
4. 사용자가 조건을 확인하면 구조 선택 이유와 장면별 화면·대사·자막·연출을 작성합니다.
5. 적용한 원리와 자료 출처를 확인하고 같은 대화방에서 대본을 수정합니다.

## 실행 — Windows / VS Code PowerShell

Python 3.12와 uv를 사용합니다. 로컬 파일과 .git은 다음 폴더에 있습니다.

```powershell
Set-Location 'C:\Users\1234v\Desktop\codyssey_work_B7-1(team_renew)'
uv python install 3.12
uv venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

.env가 이미 있으면 덮어쓰지 마세요. 생성한 무작위 값을 SECRET_KEY에 입력하고, 교육과정에서 발급받은 코디세이 API 키를 **LLM_API_KEY**에 넣습니다. 현재 팀의 키는 Anthropic 호환이므로 LLM_API_STYLE=anthropic을 사용합니다. 코디세이 요청 ID는 claude-sonnet-4이며, 2026-10-20 최소 호출에서 실제 응답 모델은 claude-sonnet-4-6으로 확인했습니다. 키는 Git·문서·채팅에 올리지 않습니다. [코디세이 설정과 확인 범위](docs/AI_SETUP.md)를 참고하세요.

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

접속: http://127.0.0.1:8000. 기본 실행 파일은 app/main.py 하나입니다. 키가 없으면 오류를 안내하며 고정 예시를 실제 AI 응답으로 보여주지 않습니다.

## 시스템 구조

```mermaid
flowchart LR
    UI[로그인 / 기획 대화 / 대본·출처] --> API[FastAPI + 인증]
    API --> STORE[소유권·버전 검사 / 짧은 저장 트랜잭션]
    STORE --> DB[(SQLite)]
    API --> COACH[사전 질문 / 생성·수정 / 결과 검증]
    COACH --> KB[검토한 개념 카드 검색]
    COACH --> LLM[서버의 코디세이 API 호출]
    LLM --> COACH
    COACH --> STORE
```

계정 스키마 → 계정 서비스 → 인증 라우터를 분리하고 새 비밀번호는 scrypt로 저장합니다. 기존 bcrypt 계정은 성공한 로그인에서 갱신하며 HttpOnly 서명 세션을 사용합니다. 제작 조건은 최근 성공 Q/A 5쌍과 별도 저장하여 오래된 조건도 유지합니다. 질문·응답·사용자·시각·실패 상태, 대본 버전과 출처를 누적 저장합니다. 서버에서 장면 시간·필수 필드·검색 카드 ID를 검증하고 같은 대화방의 동시 요청과 오래된 버전을 차단합니다.

## 환경 변수

| 이름 | 설정 |
|---|---|
| SECRET_KEY | 필수 무작위 세션 서명 키 |
| DATABASE_URL | 기본 sqlite:///./app.db, 운영은 영속 경로 |
| LLM_API_KEY | 교육과정에서 발급받은 키. 서버에서만 사용 |
| LLM_BASE_URL | https://copa.codyssey.kr/v1 |
| LLM_API_STYLE | 기본 anthropic. 키의 호환 방식에 맞춰 anthropic 또는 openai |
| LLM_MODEL | 기본 claude-sonnet-4. 코디세이의 모델 별칭 사용 |
| LLM_TIMEOUT_SECONDS | HTTP timeout, 기본 90초 |
| LLM_MAX_COMPLETION_TOKENS | 출력 예산, 기본 8000. Anthropic 요청에는 max_tokens로 전달 |
| LLM_JSON_MODE | 기본 false. openai 방식에서만 response_format 전달 |
| CHAT_TOTAL_TIMEOUT_SECONDS | AI 처리 총 대기 제한, 기본 105초 |
| KNOWLEDGE_USAGE_SCOPE | 교육용 비상업 기본. commercial이면 NC 카드 제외 |
| SESSION_HTTPS_ONLY | 로컬 HTTP false, 운영 HTTPS true |
| ENABLE_API_DOCS | 기본 false. 로컬 true이면 /docs |

.env·DB·가상환경은 Git에서 제외합니다. 예시에는 실제 키가 없습니다. Anthropic 방식은 /messages, x-api-key, 별도 system 필드로 요청합니다. 프롬프트로 JSON 출력을 지시하고 서버에서 형식·장면·출처를 검증합니다. 429 한도 초과·timeout·공급자 오류·잘못된 응답을 사용자에게 안내하며 무제한 재시도하지 않습니다.

## 이론 자료

[실제 연결 자료·PDF·이용 조건](docs/KNOWLEDGE.md)에 공개 원문 12종과 한국어 개념 카드 21개를 정리했습니다. 사진의 8개 연구 질문에 참고 자료를 연결하고, 현재 질문의 이론 이름을 우선 검색합니다. 설명 답변과 대본에 실제 검색한 출처·관련 절·확인한 PDF 쪽수·적용 한계를 표시합니다. 김미림 교수님 관련 후보 3종은 재사용 조건 확인 전 검색에서 제외합니다. [출처·변경 표시](app/data/shortform/ATTRIBUTION.md)를 유지합니다.

자료를 검색해 프롬프트에 제공하는 방식이며 모델 가중치를 학습하지 않았습니다. 카드 검토자는 Codex이며 팀원의 검토 완료를 뜻하지 않습니다. 연구의 대상·조건과 짧은 영상에 대한 팀의 제작 제안을 구분합니다. 원본 PDF 파일·해시는 로컬에 확보하지 않았으며 검토한 한국어 카드는 저장소에 보관합니다.

## 검증·DB 확인

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/check_shortform_logs.py --db app.db --user-id 1
```

실제 본인 user_id를 사용하세요. 자동 테스트는 실제 외부 AI 호출을 대역으로 분리합니다. API·SQLite 통합 테스트는 서버 의존성이 필요하며 skip을 통과로 계산하지 않습니다. 2026-10-20에는 별도 SQLite와 실제 코디세이 API로 회원가입·로그인·기획 대화·30초 대본 생성·저장·조회를 확인했습니다. 최신 실행 증거와 범위는 [검증 문서](docs/VERIFICATION.md)에 기록합니다. 다양한 입력의 대본 품질·브라우저 시각 확인·외부 공개 배포는 별도 검증 대상입니다.

## 기술 문서·협업

- [프로젝트 개요·타겟·제작 시나리오](docs/PROJECT.md)
- [화면 사용 방법](docs/USER_GUIDE.md)
- [사전 기획·템플릿·이론 기반 AI 처리](docs/AI_PROCESS.md)
- [API 요청·응답과 A/B/C 연결 규격](docs/API.md)
- [제공한 이미지의 8개 연구 주제와 챗봇 적용](docs/RESEARCH_AGENDA.md)
- [공개 원문 12종·카드 21개·검색 확인 방법](docs/KNOWLEDGE.md)
- [사용 데이터와 실제 답변 생성 흐름](docs/DATA_FLOW.md)
- [과제 요구사항별 구현·검증·남은 작업](docs/REQUIREMENTS.md)
- [코디세이 API 설정](docs/AI_SETUP.md)
- [DB·ERD·조회 가이드](docs/DATABASE.md)
- [Linux 배포·환경 변수](docs/DEPLOY.md)
- [팀 역할·실제 작업 내역](docs/TEAM.md)
- [비교 대상·독립 재구현·과거 이력](docs/UPSTREAM.md)
- [원본 소스·README 비교 결과와 올바른 공유 경로](docs/SOURCE_AUDIT.md)

main → develop → feature/c-ai-deploy에서 작업하고 PR로 통합합니다. 사용자의 요청으로 C 브랜치에서 A/B/C 초기 코드를 Codex가 함께 작성했습니다. A/B 팀원의 직접 기여로 기록하지 않습니다. 팀원별 유의미한 커밋 10회·실제 PR 머지·평가 시점 공개 서비스 URL은 팀의 실제 작업으로 완성해야 합니다.
