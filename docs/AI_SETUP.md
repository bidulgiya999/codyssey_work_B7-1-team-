# 코디세이 API 연결

사용자가 2026-10-19 Groq 사용을 취소하고 코디세이 API를 선택했다. 서버 설정·호출 코드·환경 변수·테스트를 LLM_* 규격으로 변경했다.

## 기존 프로젝트에서 확인한 규격

원본에서 가져온 main 브랜치의 app/services/llm.py와 .env.example에는 다음 값이 있었다. 현재 계정에 대해 실제 호출하거나 공식 안내를 다시 확인한 결과는 아니다.

- LLM_BASE_URL=https://copa.codyssey.kr/v1
- LLM_MODEL=gpt-5-mini
- POST /chat/completions
- Authorization: Bearer <교육과정에서 받은 키>
- 요청: model, messages, max_completion_tokens
- 응답: choices[0].message.content

공개 검색과 코디세이 페이지에서 최신 API 문서를 확인하지 못했다. 이름이 비슷한 Odyssey 등 다른 서비스의 주소·문서를 코디세이 문서로 사용하지 않는다. 교육과정에서 제공한 안내가 다르면 LLM_BASE_URL과 LLM_MODEL을 해당 값으로 설정한다.

## 환경 변수

| 이름 | 값과 역할 |
|---|---|
| LLM_API_KEY | 교육과정에서 받은 실제 키를 로컬 .env에 입력 |
| LLM_BASE_URL | 기존 프로젝트 값 https://copa.codyssey.kr/v1 |
| LLM_MODEL | 기존 프로젝트 값 gpt-5-mini. 현재 권한 확인 필요 |
| LLM_TIMEOUT_SECONDS | 기본 50초 |
| LLM_MAX_COMPLETION_TOKENS | 기본 8000. 실제 모델 한도·비용·출력에 맞춰 조정 |
| LLM_JSON_MODE | 기본 false. 프록시의 response_format 지원을 확인한 경우만 true |
| CHAT_TOTAL_TIMEOUT_SECONDS | 기본 60초 |

추론 모델은 출력 예산을 추론에도 사용할 수 있으므로 빈 응답과 finish_reason=length를 정상 대본으로 저장하지 않는다. 자동 재시도·다른 공급자로의 자동 우회는 하지 않는다. 키가 없으면 서버가 사용자에게 오류를 안내하며 실제 AI 응답을 흉내 내지 않는다. 키를 채팅·문서·Git에 넣지 않는다.

JSON은 시스템 프롬프트로 지시하고 서버에서 스키마·장면 시간·실제 검색 카드 ID를 검증한다. LLM_JSON_MODE=true일 때만 response_format={"type":"json_object"}를 추가한다. 코디세이의 지원 여부는 미확인이다.

키 누락·공급자 실패는 502, 요청 한도 초과는 429 AI_RATE_LIMIT, timeout은 504 AI_TIMEOUT이다. 실패 후 기획·대본·version은 마지막 성공 상태를 유지한다.

## 이론 자료 연결

[공개 원문·개념 카드](KNOWLEDGE.md)는 공급자와 독립적이다. 현재 질문에 관련된 최대 3개 카드를 코디세이 요청의 messages에 넣고 실제 사용한 출처를 답변·DB에 남긴다. API 키 없이 scripts/check_knowledge.py로 검색을 확인할 수 있다.

실제 키를 사용하는 코디세이 응답, 최신 모델 지원·프록시 JSON 옵션·계정 한도는 미검증이다. HTTP 계약 테스트는 대역 응답으로 주소·인증·본문·오류 처리를 확인한다.
