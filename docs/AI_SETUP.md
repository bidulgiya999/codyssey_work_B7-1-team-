# 코디세이 API 연결

## 현재 팀 설정 — Anthropic 호환

팀의 코디세이 키는 사용자가 활성 상태·Anthropic 호환이라고 확인했다. 키 라벨은 관리용 이름이며 모델 ID가 아니다. 실제 키는 로컬 .env의 LLM_API_KEY에만 입력한다.

    LLM_API_STYLE=anthropic
    LLM_BASE_URL=https://copa.codyssey.kr/v1
    LLM_MODEL=claude-sonnet-4
    LLM_TIMEOUT_SECONDS=90
    LLM_MAX_COMPLETION_TOKENS=8000
    LLM_JSON_MODE=false
    CHAT_TOTAL_TIMEOUT_SECONDS=105

2026-10-20 실제 최소 호출에서 코디세이 요청 ID claude-sonnet-4로 보냈을 때 HTTP 200, 응답의 model=claude-sonnet-4-6, stop_reason=end_turn과 비어 있지 않은 텍스트를 확인했다. 따라서 현재 코디세이를 통해 Sonnet 4.6을 사용하려면 프록시의 claude-sonnet-4 별칭을 사용한다. 이 연결 관계가 앞으로도 고정된다는 보장은 없으며 변경 시 다시 확인해야 한다.

Anthropic 공식 ID claude-sonnet-4-6을 같은 프록시에 직접 지정한 요청은 당시 404 not_found_error였다. [Anthropic 공식 모델 ID](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)와 코디세이에서 허용하는 요청 별칭을 구분한다. 다른 공급자나 모델로 자동 우회하지 않는다.

## 요청·응답 규격

[Anthropic Messages API](https://platform.claude.com/docs/en/api/messages/create)의 기본 형식을 사용하되 요청 호스트는 코디세이로 유지한다. 키를 Anthropic 직접 API나 다른 호스트에 임의 전송하지 않는다.

| 항목 | anthropic 방식 | openai 방식 |
|---|---|---|
| LLM_API_STYLE | anthropic (기본) | openai (해당 호환 키가 있을 때 명시) |
| 요청 경로 | POST /v1/messages | POST /v1/chat/completions |
| 인증 헤더 | x-api-key | Authorization: Bearer |
| 버전 헤더 | anthropic-version: 2023-06-01 | 없음 |
| 시스템 지시 | 최상위 system 필드 | messages의 system 역할 |
| 출력 예산 | max_tokens | max_completion_tokens |
| 텍스트 추출 | content의 type=text 블록 | choices[0].message.content |

두 방식 모두 LLM_BASE_URL에는 https://copa.codyssey.kr/v1처럼 /v1까지 적는다. /messages나 /chat/completions를 환경 변수에 덧붙이지 않는다.

LLM_MAX_COMPLETION_TOKENS는 기존 환경 변수 이름을 유지하며, anthropic 방식에서는 max_tokens로 변환한다. LLM_JSON_MODE는 openai 방식에서 true일 때만 response_format을 추가한다. anthropic 방식에는 이 옵션을 보내지 않는다. JSON 형식은 시스템 프롬프트로 지시하고 서버가 스키마·장면 시간·실제 검색 카드 ID를 검증한다.

Anthropic의 thinking 등 비텍스트 블록은 답변으로 반환하지 않는다. max_tokens로 잘린 응답, tool_use·refusal 등 미완료 응답, 빈 텍스트나 잘못된 형식은 정상 대본으로 저장하지 않는다. 자동 재시도는 하지 않는다. 실제 대본 생성이 기존 50초 제한을 넘겨 HTTP timeout을 90초, 대화 처리 전체 timeout을 105초로 조정했다. 전체 제한의 설정 상한은 120초다.

## 403 오류 원인과 확인 범위

기존 프로젝트는 gpt-5-mini와 OpenAI 호환 /chat/completions를 기본으로 사용했다. 이번 키로 해당 경로에 요청했을 때 gpt-5-mini·claude-sonnet-4·claude-sonnet-4-6 모두 403 permission_denied였다. 키가 모델 목록 조회에 성공하더라도 다른 호환 방식의 채팅 요청이 허용되는 것은 아니다.

Anthropic 호환 /messages로 변경한 뒤 claude-sonnet-4 요청이 성공했다. 따라서 앞선 403만으로 계정 자체의 채팅 권한이 없다고 판단할 수 없다. 이번 설정에서는 키의 호환 방식과 호출 규격의 불일치를 고쳐 해결했다. 향후 별도 계정·키·모델의 권한을 보장하는 결과는 아니다.

401은 앱의 502 AI_AUTH_ERROR, 403은 502 AI_ACCESS_DENIED로 구분한다. 사용자의 웹 로그인과 공급자 인증 오류를 구분하기 위해 앱 상태는 502로 유지한다. 429는 AI_RATE_LIMIT, timeout은 504 AI_TIMEOUT이다. 실패 후 기획·대본·version은 마지막 성공 상태를 유지한다. 로그에는 요청 ID·upstream_status 등 진단 정보만 남기며 키나 공급자 오류 원문은 쓰지 않는다.

## 적용과 재시작

.env가 이미 있으면 예시 파일로 덮어쓰지 않는다. SECRET_KEY와 LLM_API_KEY는 유지하고 위 모델·호환 설정만 변경한다. .env는 Git에서 제외한다. 키·세션 서명 키를 채팅·문서·Git에 넣지 않는다.

실행 중인 서버 터미널에서 Ctrl+C로 종료한 뒤 프로젝트 폴더에서 다시 실행한다. .env 변경은 --reload만으로 반영된다고 가정하지 않는다.

    .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

## 이론 자료와 검증

[공개 원문·개념 카드](KNOWLEDGE.md)는 공급자와 독립적이다. 현재 질문에 관련된 최대 3개 카드를 시스템 지시와 함께 서버 요청에 제공하고 실제 사용한 출처를 답변·DB에 남긴다. API 키 없이 scripts/check_knowledge.py로 검색을 확인할 수 있다.

HTTP 계약 테스트는 두 호환 방식의 주소·인증·본문·응답과 실패 처리를 대역으로 검증한다. 실제 API 검증 결과와 남은 검증 항목은 [검증 문서](VERIFICATION.md)에 구분해 기록한다.
