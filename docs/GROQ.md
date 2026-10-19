# Groq Console 연동

이 서비스는 [Groq Console](https://console.groq.com/home)에서 발급한 키를 사용한다. [API Keys](https://console.groq.com/keys)에서 사용자가 직접 발급하고 프로젝트 루트의 .env에 GROQ_API_KEY를 설정한다. 실제 키를 소스·GitHub·문서·채팅에 넣지 않는다.

| 환경 변수 | 예시·역할 |
|---|---|
| GROQ_API_KEY | 로컬에 실제 발급 키 입력, .env.example은 빈 값 |
| GROQ_BASE_URL | https://api.groq.com/openai/v1 |
| GROQ_MODEL | openai/gpt-oss-20b. 현재 팀 계정에서 사용 가능한 모델 확인 |
| GROQ_TIMEOUT_SECONDS | 기본 30초 |
| GROQ_MAX_COMPLETION_TOKENS | 기본 6000. 계정 한도·응답 품질 확인 후 조정 |
| CHAT_TOTAL_TIMEOUT_SECONDS | 기본 40초 |

서버가 `/chat/completions`에 Bearer 키·system/대화 메시지·출력 예산·`response_format={"type":"json_object"}`를 보낸다. 브라우저에는 결과와 검증된 출처만 반환한다. JSON 모드는 구문을 위한 설정이며 Brief/ScriptDraft 스키마·시간·출처 ID 검사는 서버에서 별도로 수행한다.

키 누락·공급자 오류는 502, 요청 한도 초과는 429 AI_RATE_LIMIT, timeout은 504 AI_TIMEOUT을 반환한다. 잘린 응답이나 빈 응답은 정상 대본으로 저장하지 않는다. 자동 재시도는 하지 않는다. 실패 후 기획·대본·version은 마지막 성공 상태를 유지한다.

지원 모델은 변경될 수 있다. 현재 예시 모델의 사용 가능 여부는 Console에서 확인한다. 예전 인터넷 예제의 모델 이름을 그대로 복사하지 않는다. 2026-10-19 공식 문서를 확인했으며 실제 계정에 대한 API 호출은 하지 않았다.

근거: [호환 API 주소](https://console.groq.com/docs/openai), [JSON 출력 모드](https://console.groq.com/docs/structured-outputs), [GPT OSS 20B](https://console.groq.com/docs/model/openai/gpt-oss-20b), [모델 지원 종료 안내](https://console.groq.com/docs/deprecations).
