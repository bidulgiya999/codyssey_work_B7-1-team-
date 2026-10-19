# 검증 현황 — 2026-10-19

## 실행 결과

- 새 폴더에 소스·Git 이력 복사, C 브랜치 유지, 원본 미변경.
- 기획·검색·문맥·응답·출처·장면 시간·타임아웃 등 **코어 테스트 26개 통과**.
- ASGI·SQLite 통합 테스트 12개 작성. 의존성 부재로 **12개 skip**. 통과로 계산하지 않음.
- JavaScript 구문 검사 통과. Python 구문·JSON·자료 연결 검증은 scripts/verify_reels.py로 확인한다.

## 환경 제한

PyPI DNS 오류로 FastAPI·SQLAlchemy·httpx 등 서버 의존성을 설치하지 못했다. 기본 Windows asyncio 루프도 이 실행 호스트에서 내부 loopback 소켓 생성 시 정지하는 현상을 최소 예제로 확인했다. 코어 테스트는 네트워크 I/O를 거절하는 `REELS_TEST_MEMORY_LOOP=1` 테스트 루프를 사용했다. 타이머·취소·코루틴을 확인하지만 서버 소켓/실제 이벤트 루프 동작의 증거가 아니다. 운영 코드는 이 테스트 루프를 사용하지 않는다.

```powershell
$env:REELS_TEST_MEMORY_LOOP = '1'
# REELS_TEST_TMPDIR에 쓰기 가능한 테스트 임시 경로 지정 후 실행함.
python -m unittest discover -s tests_reels -v
```

## 후속 검증

일반 환경에서 requirements-reels-dev.txt를 설치하고 API 테스트 12개를 실제 실행한다. 실제 AI의 JSON 형식·응답 품질·지연·수정, PC/모바일 브라우저, Linux HTTPS·영속 DB·외부 접속 URL은 미확인이다. 기존 문서의 과거 테스트 결과를 이번 결과로 옮겨 적지 않는다.

팀이 카드 내용을 재검토하고 김미림 교수님 자료의 원문·이용 범위를 확보해야 한다. A/B/C 각자의 실제 커밋·PR 검토·머지와 개인별 10회 기여 요건은 별도다. 이번 초안을 세 사람의 커밋으로 나누어 기록하지 않았다.
