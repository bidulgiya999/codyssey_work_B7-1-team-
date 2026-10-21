# 팀 구성·역할·인수인계

사용자가 2026-10-21 확인한 이름과 역할표를 기준으로 한다. 서비스 주제는 **영상 이론 기반 인스타 릴스 제작 코치**다.

| 담당 | 이름 | 역할 | 담당 문서 |
|---|---|---|---|
| A | 이송하 | 웹 화면·서비스 기획 | 프로젝트 개요, 타겟 사용자, 사용 시나리오, 화면 사용 방법 |
| B | 김시현 | 인증·DB·대화 기록 | DB 구조, 인증·기록 조회 API 명세, DB 확인 가이드 |
| C | 황승재 | AI 챗봇·서버 배포 | 시스템 구조, 채팅 API 명세, AI 처리 방식, 배포·실행 방법 |

A·B의 GitHub ID는 아직 제공받지 않았다. C의 계정은 bidulgiya999다. 다른 사람의 GitHub ID나 개인별 실적을 추정하지 않는다.

## A — 이송하: 사용자가 기획하고 결과를 이해하는 화면

- 회원가입·로그인 화면, 대화 화면, 이전 대화 조회 화면을 맡는다.
- 제작 조건 입력 방식과 결과 형식을 정한다. 부족한 조건 1~2개 질문 → 조건 요약 → 사용자 확인 → 장면별 대본·근거의 흐름을 보여준다.
- 로딩·오류·재시도 안내와 화면/API 연결을 확인한다. 연령만으로 취향을 단정하는 문구는 쓰지 않는다.
- 담당 파일: app/templates/shortform/, app/static/css/shortform.css, app/static/js/auth.js·common.js·shortform.js.
- 담당 문서: PROJECT.md, USER_GUIDE.md, README의 서비스 설명·시나리오.
- 완료 기준: PC·모바일에서 가입·로그인·대화·기록·대본 생성/수정이 가능하고, AI 오류와 출처가 안전하게 표시된다.
- 권장 작업 브랜치: feature/a-reels-ui.

## B — 김시현: 계정·기록의 저장과 접근 제어

- 회원가입·로그인·로그아웃 API, 비밀번호 해시, 로그인 상태 확인을 맡는다.
- 사용자·대화방·질문/응답·대본 버전 DB와 저장/조회, 타인 기록 접근 차단을 맡는다.
- DB 저장 성공·실패 로그와 사용자별 기록 조회, 확인 스크립트를 유지한다.
- 담당 파일: app/routers/auth.py·conversations.py, app/schemas/accounts.py, app/services/accounts.py, app/security.py, app/dependencies.py, app/database.py, app/models/, app/services/shortform/store.py, scripts/check_shortform_logs.py.
- 담당 API: /api/auth/*, /api/me, /api/conversations*, /api/me/chats. URL과 요청·응답 예시는 API.md에 있다.
- 담당 문서: DATABASE.md, API.md의 인증·기록 부분.
- 완료 기준: 비로그인/타인 접근 차단, 중복 가입·잘못된 입력 처리, 기존 계정 호환, DB 성공/실패와 대본 버전 보존을 검증한다.
- 권장 작업 브랜치: feature/b-accounts-history.

## C — 황승재: 사전 기획·이론 기반 대본·운영

- FastAPI 채팅 API와 코디세이 Anthropic 호환 API 연결을 맡는다. 실제 키는 서버 .env에만 둔다.
- 주제·목적·타겟 세그먼트·연령·등장인물·연출·길이·핵심 메시지를 대화로 정리하고 최근 문맥을 유지한다.
- 조건 확인 후 제작 템플릿 후보와 관련 이론 자료를 제공해 장면별 대본·연출·적용 이유를 작성한다.
- 입력 검증, timeout·권한·한도·응답 형식 실패 처리, 요청 수신·AI 호출/응답 로그를 맡는다.
- Linux 실행·환경 변수·HTTPS·영속 SQLite 배포와 외부 접속 검증을 맡는다.
- 담당 파일: app/routers/shortform.py, app/services/llm.py, app/services/shortform/coach.py·schemas.py·structures.py·knowledge.py·research.py, app/data/shortform/, deploy/, app/main.py·config.py.
- 담당 문서: AI_PROCESS.md, AI_SETUP.md, API.md의 채팅 부분, DEPLOY.md, VERIFICATION.md, RESEARCH_AGENDA.md·KNOWLEDGE.md.
- 완료 기준: 실제 API 대본 생성/수정, 조건·문맥·출처 검증, 실패 후 상태 보존, 평가 시 외부 URL과 서버 로그 확인.
- 현재 브랜치: feature/c-ai-deploy.

## 공통 연결 규칙

1. A는 로그인 상태의 같은 출처 쿠키로 API를 호출한다. 브라우저가 user_id나 API 키를 보내지 않는다.
2. B는 본인 대화방과 version을 확인하고 최근 성공 Q/A 5쌍·기획·최신 대본을 C에 넘긴다. AI 대기 중 DB 쓰기 트랜잭션을 유지하지 않는다.
3. C는 JSON·장면 시간·실제 검색 카드 ID를 검증한 결과만 B에 넘긴다. B의 저장 성공 후 A에 반환한다.
4. A는 phase=ready에서 사용자가 확인했을 때만 generate를 호출한다. 수정 요청에는 현재 base_script_id를 포함한다.
5. 공통 파일·API·DB 필드 변경은 PR에서 상대 담당자와 먼저 맞춘다. URL을 유지한 채 내부 구현을 바꾸는 것도 인수인계에 기록한다.

## 실제 작업 이력과 앞으로의 개인별 기여

2026-10-19~20: C 작업 브랜치에서 사용자의 요청으로 Codex가 A/B/C 통합 초안을 작성하고 실제 AI 연결을 점검했다.

2026-10-21: 사용자의 새 구현 요청에 따라 인증 스키마·계정 서비스·라우터·비밀번호 저장·세션 식별·DB 연결·브라우저 계정 연동을 재구현했다. B의 자원 API와 C의 채팅 API를 분리하고, 화면·프롬프트·문서의 인스타 릴스 주제를 확정했다. 이 작업은 C 브랜치에서 AI 보조로 작성한 통합 초안이며 A·B가 직접 작성/검토했다는 뜻이 아니다.

각 팀원은 맡은 영역의 실제 개선과 테스트·리뷰를 수행하고 유의미한 커밋 10회 이상을 자신의 계정으로 남긴다. 원본 팀의 커밋이나 자동 작성분을 A/B/C 개인 실적으로 나누어 기록하지 않는다. 개인별 작업 요약은 실제 PR·커밋 링크와 맞춰 갱신한다.

브랜치 운영: 기능 브랜치 → develop 통합 PR → main 제출/배포 PR. 팀 검토 전 공유 기본 브랜치를 자동 교체하지 않는다. 서비스 계정 초대·GitHub 권한은 저장소 소유자가 실제 팀 계정을 확인해 설정한다.
