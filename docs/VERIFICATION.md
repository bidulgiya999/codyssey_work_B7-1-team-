# 인스타 릴스 제작 코치 검증 — 2026-10-21

## 현재 코드의 자동 검증

- Python 76개 테스트 통과, skip 없음. 코어 36, API/SQLite 19, HTTP 계약 14, 계정/기존 DB 호환 4, 제작 템플릿 3개다.
- Node 브라우저 클라이언트 검사 9개 통과. JSON 요청·204 로그아웃·504 상태·대기 취소·안전한 오류 표시·가입·비밀번호 확인·UTF-8 길이·로그인 실패를 DOM 대역으로 확인했다. 실제 브라우저 시각 검사는 아니다.
- Python 실행: .venv/Scripts/python.exe -m unittest discover -s tests -v. 로컬 기록은 Git에서 제외되는 tmp/reels-independent-final-tests.log에 있다.
- Node 실행: node tests/browser_clients.mjs. common.js/auth.js/shortform.js의 구문 검사도 통과했다.
- scripts/verify_shortform.py의 33개 Python 파일·JSON·21개 카드·README 링크 검사와 git diff --check를 통과했다.
- 새 비밀번호의 scrypt 검증·서로 다른 salt·오류/비정상 파라미터 거절, 기존 bcrypt 로그인과 ID 유지, 기존 SQLite VARCHAR(60) 열의 갱신을 확인했다.
- 비로그인/타인 접근 차단, 중복 가입·이메일 정규화, 잘못된 유니코드, 삭제 계정의 쿠키 재사용 차단을 확인했다.
- AI 호출·입력/스키마·출처·시간·대본 버전·처리 잠금·DB 실패 후 복구는 대역을 사용하는 통합 시험이며 실제 유료 호출로 계산하지 않는다.

## 원본과 구분하는 검사

[코드 비교 기록](SOURCE_AUDIT.md)에 기준 커밋·현재 구현 범위·한계를 기록한다. 가져왔던 develop 커밋과 비교 대상 저장소의 현재 main을 각각 대조해 비어 있지 않은 동일 소스 파일과 전체 Python AST 일치가 0건임을 확인했다. 이 결과를 모든 공통 코드 조각이 없다는 보장이나 저작권 판정으로 사용하지 않는다.

.env는 Git에서 제외되며 실제 API 키와 SECRET_KEY가 현재 추적/추가 예정 파일 또는 도달 가능한 로컬 Git 이력에 포함되지 않았음을 값 출력 없이 점검했다. Git 실습 파일 test_amend.txt는 이번 서비스 변경에 포함하지 않는다.

## 실제 AI 실행 증거

2026-10-20 실제 키로 코디세이 Anthropic 호환 /v1/messages에 claude-sonnet-4를 요청했을 때 응답 model=claude-sonnet-4-6과 HTTP 200을 확인했다. 직접 claude-sonnet-4-6을 프록시에 지정하면 404, 같은 키를 OpenAI 호환 경로에 쓰면 403이었다.

당시 별도 SQLite와 실제 FastAPI ASGI 앱에서 회원가입·로그인·사전 질문·조건 요약·30초 대본 생성·기록 조회를 확인했다. 성공 대화 3건, 대본 1건, 장면 6개·출처 1종이 저장됐다. 증거는 tmp/live-sonnet46-416e3692/의 report.json·sample-script.json·verification.db에 있다. 원래 사용자의 app.db를 사용한 시험이 아니다.

2026-10-21 재구현 이후에도 별도 SQLite와 실제 AI로 새 회원가입·로그인·대화방 생성·사전 질문 2개·조건 요약·30초 대본 생성·기록 조회를 다시 확인했다. 성공 대화 3건, 대본 1건, 장면 5개·출처 1종을 저장했다. 결과는 tmp/live-sonnet46-657d4cb5/report.json과 sample-script.json에 있다. 기존 사용자 DB를 사용하거나 AI를 대역으로 바꾼 실행이 아니다. 각 실행의 실패를 성공으로 합산하지 않는다. 모든 입력에서 응답 시간·형식·품질을 보장하는 시험은 아니다.

## 이전 CI와 남은 검증

이전 b7469f90a39d13cb010a8a4825de981da66d04d0의 [Linux/Python 3.12 CI](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/actions/runs/39231795091)는 당시 59개 테스트를 통과했다. 이전 코드의 증거이며 이번 재구현 코드의 CI 결과로 대신하지 않는다.

PC/모바일 실제 브라우저 시각 확인, 다양한 조건의 대본 품질 비교, PDF 원본 확보·팀 검토, Linux 운영 HTTPS·영속 DB·외부 접속 URL, 팀원별 실제 커밋과 리뷰/PR 병합은 별도 확인 대상이다. PDF 페이지를 웹에서 확인한 것과 파일 전체 학습·OCR·파인튜닝을 구분한다.

## 보관·공유

로컬 폴더는 C:\Users\1234v\Documents\Codex\codyssey_work_B7-1(team_work)이며 작업 브랜치는 feature/c-ai-deploy다. 외부 공유는 [현재 구현 브랜치](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/tree/feature/c-ai-deploy)를 사용한다. 기본 브랜치 main의 초기 README를 새 서비스로 교체하려면 검토된 PR을 통합해야 한다. 기존 PR #1은 2026-10-21 확인 시 닫혀 있고 병합되지 않았다.
