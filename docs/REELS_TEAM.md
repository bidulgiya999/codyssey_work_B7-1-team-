# 팀 역할과 실제 작업 기록

팀원은 A/B/C 총 3명이며 사용자는 C 담당이다. 이름·GitHub ID는 팀 확인 후 기입한다. 다른 두 팀원의 이름이나 커밋을 임의로 만들지 않는다.

| 담당 | 예정 책임 | 이번 초기 구현 파일 |
|---|---|---|
| A | 서비스 기획·UX/UI·화면과 API 연결·사용 설명 | templates/reels, static/css/reels.css, static/js/reels.js |
| B | 인증·DB·대화·대본 저장/조회·소유권 | 기존 auth/security/user 재사용, models/reels.py, services/reels/store.py, DB 확인 스크립트 |
| C | 채팅 API·사전 기획·이론 검색·프롬프트·AI·예외·로그·Linux | routers/reels.py, services/reels/coach.py·schemas.py·knowledge.py, reels_main.py, 데이터·배포·문서 |

2026-10-19: 사용자 요청으로 Codex가 C 작업 브랜치에서 A/B/C 초기 통합 코드를 작성했다. 위 표는 코드의 담당 영역이며, A·B 팀원이 직접 구현하거나 커밋했다는 뜻이 아니다. 기존 인증·UI·AI 클라이언트와 Git 이력은 원본 `L-jy16/ai_chatbot`에서 가져왔다. 원본 저자의 기여를 현재 팀의 개인별 실적으로 바꾸지 않는다.

브랜치 흐름: main(제출/배포 기준) → develop(통합) → feature/c-ai-deploy(현재 작업). 이후 A·B는 별도 작업 브랜치에서 수정하고 develop에 PR을 연다. 팀 합의 전에는 이번 통합 초안을 develop에 자동 머지하지 않는다. 기존 저장소의 동료를 새 저장소에 자동 초대하지 않았다.

과제의 ‘팀원별 유의미한 커밋 10회 이상’은 각 팀원의 실제 개선 작업으로 채워야 한다. 이번 자동 작성분을 세 사람의 작업으로 나누어 기록하거나, 의미 없이 커밋을 분할하지 않는다. 팀원별 작업 요약은 실제 PR·커밋과 맞춰 보완한다.

검토 순서: A의 질문 문구·출처 표시 → B의 소유권·버전·복구 → C의 실제 AI 출력·timeout·Linux 검증 → 공동 시연·평가 문서.
