# 릴스 대본 코치 검증 현황 — 2026-10-19

## 최신 실행 결과

- [Linux / Python 3.12 CI](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/actions/runs/39228574869)에서 **50개 테스트 모두 통과**, skip 없음.
- 검증 커밋: `031a256eabb1cc2569a98d8bbc109d4ba76aead8`.
- 로그: `Ran 50 tests in 11.136s` / `OK`.
- 코어 29개, API·SQLite 통합 13개, Groq HTTP 계약 8개. 서버 의존성 import 확인과 scripts/verify_reels.py도 통과했다.
- 기획 대화·대본 생성에 이미지의 8개 연구 주제가 전달되는지, 연구 질문을 검증된 결과로 표시하거나 출처로 인용하면 거절하는지 검증했다.
- 가입·로그인·로그아웃, 비로그인/타인 접근 차단, 대화방 문맥 분리, 저장 실패·timeout·Groq 429 후 상태 보존, 동시 처리 lease, 생성·수정 버전과 출처 저장을 검증했다.
- Groq 주소·모델·인증·JSON Object Mode 전달과 키 누락·timeout·429·HTTP 실패·잘못된 JSON·빈 응답·잘린 응답 처리를 대역 HTTP 응답으로 검증했다.

app.main:app이 기본 실행 파일이다. 화면·AI 처리·문서는 릴스 대본 코치로 통일했다. 이전 Groq 전환 커밋 `628f768c43fe0a70731646f557288e7d7b267c9a`도 [47개 테스트가 통과](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/actions/runs/39228039496)했다.

## 로컬 환경과 확인 범위

새 폴더에 소스와 .git을 보관하며 feature/c-ai-deploy 브랜치를 GitHub와 동기화했다. 원본 Desktop 저장소는 변경하지 않았다. JavaScript 구문, Python 구문·JSON·자료 연결·README 링크 검증을 통과했다.

이 실행 호스트에서는 PyPI DNS 오류로 FastAPI·SQLAlchemy·httpx 등 서버 의존성을 설치하지 못했다. Windows asyncio 기본 루프도 내부 loopback 소켓 생성 시 정지하는 현상을 최소 예제로 확인했다. 로컬 코어 29개는 I/O를 거절하는 REELS_TEST_MEMORY_LOOP=1 테스트 루프에서 통과했고, 나머지 21개는 의존성 부재로 skip되었다. **skip을 통과로 계산하지 않는다.** 위 CI는 실제 설치한 서버 의존성과 일반 이벤트 루프에서 전체 테스트를 실행했다. 운영 코드는 테스트 루프를 사용하지 않는다.

## 남은 검증과 팀 작업

실제 Groq API 호출·모델의 대본 품질·지연·수정, Windows 로컬 서버 실행, PC/모바일 브라우저 화면, Linux 운영 HTTPS·영속 DB·외부 접속 URL은 미확인이다. 테스트는 AI 응답을 대역으로 주입하며 실제 유료 API를 호출하지 않았다.

PDF 업로드·OCR·모델 가중치 학습을 구현한 상태는 아니다. 이미지의 연구 질문은 대본 점검 기준으로 전달하고, 현재 인용 가능한 개념 카드는 별도로 검색한다. 팀이 카드 내용을 재검토하고 추가 원문·이용 범위를 확보해야 한다.

A/B/C 각자의 실제 커밋·PR 검토·머지와 개인별 10회 기여 요건은 별도다. 초안 작업을 세 사람의 커밋으로 나누어 기록하지 않았다. develop으로의 PR은 검토 대기 상태다.
