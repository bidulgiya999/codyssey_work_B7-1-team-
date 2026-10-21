# 릴스 대본 코치 검증 현황 — 2026-10-20

## 최신 코드 검증

- Windows 로컬의 설치된 의존성과 일반 asyncio 이벤트 루프에서 **65개 테스트 모두 통과, skip 없음**. 코어 36개, API·SQLite 통합 15개, 코디세이 HTTP 계약 14개다.
- 실행: 프로젝트 폴더에서 `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`. 기록은 Git에서 제외되는 tmp/anthropic-tests-final.log에 보관했다.
- Anthropic Messages 요청의 주소·x-api-key·버전·별도 system·max_tokens, 텍스트 블록 추출과 thinking 제외, 잘림·미완료 응답·timeout·401·403·429 처리를 추가 검증했다. OpenAI 호환 요청도 별도 대역 테스트로 유지한다.
- scripts/verify_reels.py의 Python 구문·자료 연결·README 링크 검사와 git diff --check도 통과했다. 대역 테스트는 실제 API 성공으로 계산하지 않는다.

## 이전 Linux CI 증거

- [Linux / Python 3.12 CI 실행](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/actions/runs/39231795091): **59개 테스트 모두 통과, skip 없음**.
- 당시 검증 커밋: b7469f90a39d13cb010a8a4825de981da66d04d0. 위 65개 로컬 검증과 구분한다.
- 코어 36개, API·SQLite 통합 14개, 코디세이 HTTP 계약 9개. 서버 의존성 import 사전 확인과 scripts/verify_reels.py도 통과했다.
- 앞선 자료 연결 커밋 acc71a6f9f08afea03edf683138f4f70622657c6도 [59개 테스트 통과](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/actions/runs/39231651192). 그 후 특정 이론 질문에 관련 없는 맥락 카드가 섞이지 않도록 보완했다.

## 검증한 내용

- 로그인·로그아웃·가입, 비로그인/타인 접근 차단, 사용자·대화방별 기록 분리.
- 최근 문맥과 기획 조건 보존, 조건 확인 전 생성 방지, 대본 생성·수정과 버전·출처 저장.
- 동시 요청 lease, 오래된 버전 차단, AI timeout·429·응답 형식 오류·DB 실패 후 상태 보존.
- 공개 원문 12종·개념 카드 21개에 대한 검색과 8개 연구 주제의 연결.
- 한국어 띄어쓰기·영문 별칭, 현재 질문에 명시된 이론을 오래된 맥락보다 우선 검색.
- 검색 카드가 AI 요청에 전달되고 실제 카드 ID·저자·URL·라이선스·검토한 PDF 쪽수가 응답과 SQLite 대화 로그에 저장되는 ASGI 통합 흐름.
- 확인하지 않은 연구 질문·검색되지 않은 카드의 인용 거절, 근거 없는 설명의 확인 불가 안내.
- NC 카드의 상업용 scope 제외, 허용하지 않은 라이선스의 검색 제외, PDF 페이지 범위 검증.
- 코디세이 요청 주소·Bearer 키·모델·출력 예산, 기본 response_format 미전송과 명시적으로 켠 경우의 전송. 빈 응답·잘림·HTTP 실패·timeout·429 처리를 대역 HTTP로 검증.
- Python 구문·JSON·자료 연결·문서의 로컬 링크·JavaScript 구문과 Git 변경의 공백 검사 통과.

## 로컬 보관과 실행 호스트 제한

소스와 .git은 C:\Users\1234v\Documents\Codex\codyssey_work_B7-1(team_work)에 보관한다. 연결 수정은 feature/c-ai-deploy 브랜치의 로컬 커밋으로 보관하며, GitHub 반영은 별도 push가 필요하다. 바탕화면 원본 저장소는 변경하지 않았다. .env·DB·tmp는 Git에서 제외된다.

2026-10-19에는 DNS·소켓 제한과 의존성 부재로 로컬 코어 테스트만 실행했고 API 테스트는 skip되었다. 2026-10-20에는 의존성이 설치되어 있고 네트워크 접근을 허용받아 일반 이벤트 루프로 위 65개를 모두 실행했다. 이전 제한을 현재의 실행 결과로 혼동하지 않는다. 운영 코드는 테스트용 메모리 이벤트 루프를 사용하지 않는다.

## 실제 API 연결·통합 확인

실제 키로 코디세이 Anthropic 호환 /v1/messages를 최소 호출하여 요청 ID claude-sonnet-4가 당시 응답 model=claude-sonnet-4-6으로 연결됨을 확인했다. 직접 claude-sonnet-4-6을 지정하면 404, OpenAI 호환 /chat/completions에 같은 키를 쓰면 403이었다. 최신 전체 모델·계정 한도·OpenAI 호환 JSON 옵션은 미확인이다. 자세한 연결 규격은 [코디세이 설정](AI_SETUP.md)을 따른다.

- FastAPI TestClient(실제 ASGI 앱)·별도 SQLite 파일·실제 코디세이 API를 연결해 회원가입 201, 로그인 200, 대화방 생성 201, 사전 질문 200, 조건 요약 200, 대본 생성 200, 기록 조회 200을 확인했다.
- 최종 예시 소재는 책상 정리였다. 사전 질문은 2개였고, 확인한 30초 조건으로 6개 장면과 출처 1종을 생성했다. 장면 구간은 0–5, 5–9, 9–16, 16–21, 21–26, 26–30초로 서버 검증을 통과했다. SQLite에는 성공 대화 3건·대본 1건이 누적됐다.
- 해당 최종 실행 증거는 Git에서 제외되는 tmp/live-sonnet46-416e3692/report.json, sample-script.json, verification.db에 보관한다. 기존 사용자의 app.db와 계정·대화는 변경하지 않았다. AI 호출을 대역으로 바꾸지 않았다. 최종 실행의 사전 질문·조건 요약·대본 생성 지연 시간은 각각 약 6.5초·6.0초·34.0초였다.
- 앞선 실행에서는 기존 50초 제한으로 대본 생성이 timeout됐고, 별도 실행에서는 기획 추출 응답이 형식 검증에 실패했다. 실패를 성공 건수에 포함하지 않았다. timeout을 90/105초로 조정하고 기획 단계에서 대본을 미리 쓰지 않도록 출력 지시를 보완했다. 형식·출처 검증과 사용자 확인 단계는 유지한다. 모든 입력에 대한 응답 품질·시간을 보장하는 시험은 아니다.

## 아직 확인하지 않은 부분

공개 PDF 일부는 웹 도구로 본문·페이지를 확인했다. 로컬 DNS 제한으로 원본 PDF 바이트·SHA-256은 확보하지 못했으며, 검토한 한국어 카드만 저장소에 보관한다. 원문 전체 학습·파인튜닝·PDF 업로드/OCR 자동화는 하지 않았다. 자료의 적용 범위는 [실제 연결 목록](KNOWLEDGE.md)에 명시했다.

Windows에서 실제 서버 실행, PC/모바일 브라우저의 시각 확인, Linux 운영 HTTPS·영속 DB·외부 접속 URL은 별도 검증 대상이다. A/B/C의 실제 개인별 10회 커밋과 PR 검토·머지도 팀이 진행해야 한다. develop으로의 PR은 초안 검토 대기 상태다.
