# 릴스 대본 코치 검증 현황 — 2026-10-19

현재 기본 실행 파일을 app.main:app으로 통일하고 Groq 연동으로 변경했다. 과거 주제의 화면·기능·문서·테스트·도표는 제거했다. 변경 후 검증 대상은 코어 26개, API/SQLite 13개, Groq HTTP 계약 8개로 총 47개다. 최신 CI 확인 결과는 아래에 추가한다.

## 실행 결과

- 새 폴더에 소스·Git 이력 복사, C 브랜치 유지, 원본 미변경.
- 기획·검색·문맥·응답·출처·장면 시간·타임아웃 등 **코어 테스트 26개 통과**.
- 로컬에서는 ASGI·SQLite 통합 테스트 12개가 의존성 부재로 skip되었다. 이후 **GitHub Actions의 Linux/Python 3.12에서 코어 26개 + API·SQLite 12개, 총 38개가 skip 없이 모두 통과**했다.
- JavaScript 구문 검사 통과. Python 구문·JSON·자료 연결 검증은 scripts/verify_reels.py로 확인한다.

## 환경 제한

PyPI DNS 오류로 FastAPI·SQLAlchemy·httpx 등 서버 의존성을 설치하지 못했다. 기본 Windows asyncio 루프도 이 실행 호스트에서 내부 loopback 소켓 생성 시 정지하는 현상을 최소 예제로 확인했다. 코어 테스트는 네트워크 I/O를 거절하는 `REELS_TEST_MEMORY_LOOP=1` 테스트 루프를 사용했다. 타이머·취소·코루틴을 확인하지만 서버 소켓/실제 이벤트 루프 동작의 증거가 아니다. 운영 코드는 이 테스트 루프를 사용하지 않는다.

```powershell
$env:REELS_TEST_MEMORY_LOOP = '1'
# REELS_TEST_TMPDIR에 쓰기 가능한 테스트 임시 경로 지정 후 실행함.
python -m unittest discover -s tests -v
```

## 후속 검증

Windows 로컬 실행은 requirements-dev.txt 설치 후 별도 확인한다. 실제 Groq 모델의 JSON 형식·응답 품질·지연·수정, PC/모바일 브라우저, 운영 Linux HTTPS·영속 DB·외부 접속 URL은 미확인이다. 테스트에서는 AI 응답·실패를 대역으로 주입하며 실제 유료 API를 호출하지 않았다.

## 이전 단계의 CI 증거

- [전체 38개 테스트 통과한 실행](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/actions/runs/39225589443).
- 검증 커밋: `265b7c3cf6b0c979a881b0f7dec410626b3cbec8`.
- 로그 결과: `Ran 38 tests in 13.290s` / `OK`. 패키지 import 사전 확인을 통과했으며 skip 표시 없음.
- FastAPI 0.146.0, SQLAlchemy 2.1.5, Pydantic 2.14.1, httpx 0.28.1, bcrypt 5.0.0 환경에서 확인. CI는 일반 이벤트 루프를 사용함.
- 가입·로그인·로그아웃, 비로그인/타인 접근 차단, 대화방 문맥 분리, 저장 실패·timeout 후 상태 보존, 동시 처리 lease, 생성·수정 버전과 출처 저장을 검증함.

팀이 카드 내용을 재검토하고 김미림 교수님 자료의 원문·이용 범위를 확보해야 한다. A/B/C 각자의 실제 커밋·PR 검토·머지와 개인별 10회 기여 요건은 별도다. 이번 초안을 세 사람의 커밋으로 나누어 기록하지 않았다.
