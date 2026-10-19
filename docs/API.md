# 릴스 대본 코치 API v1

실행 대상: `app.main:app`. 코디세이 API를 서버에서 호출한다. 날짜: 2026-10-19.

## 인증·오류

같은 출처의 서명된 HttpOnly 세션 쿠키를 사용한다. 인증은 기존 `app/routers/auth.py`와 bcrypt를 재사용한다. API에서 인증 사용자 ID를 결정하며 브라우저가 보낸 user_id는 권한 근거로 받지 않는다. 운영 HTTPS에서 `SESSION_HTTPS_ONLY=true`를 설정한다. 로그아웃은 쿠키를 지우는 방식으로, 탈취한 서명 쿠키의 서버 측 개별 폐기는 초기 범위에 없다.

오류 예시:

```json
{"error":"AI_TIMEOUT","message":"응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요.","request_id":"server-generated-uuid"}
```

401 비로그인, 404 타인의 대화방·없는 자원, 409 처리 중/버전 충돌/대본 불일치, 422 입력 검증, 429 코디세이 한도 초과, 502 AI 실패·응답 검증 실패, 503 DB·자료 준비 실패, 504 AI timeout. 응답의 `X-Request-ID`와 오류·서버 로그 ID를 연결한다. 원문 질문·AI 본문·비밀번호·API 키는 운영 이벤트 로그에 쓰지 않는다.

## 엔드포인트

| 메서드·경로 | 요청 | 응답·권한 |
|---|---|---|
| POST /api/auth/signup | email, password | 201 `{id,email}`. 8자 이상·72 UTF-8 바이트 이하 비밀번호 |
| POST /api/auth/login | email, password | 200 `{id,email}`, 세션 쿠키 |
| POST /api/auth/logout | 없음 | 로그인 필요, 204 |
| GET /api/me | 없음 | 본인 `{id,email,ai_provider,ai_configured}` |
| POST /api/conversations | `{title?}` | 본인 대화방, 201. 제목 기본 ‘새 릴스 기획’ |
| GET /api/conversations | limit=20, offset=0 | 본인 목록 `{items,limit,offset}`, 최신순. limit 1~100 |
| GET /api/conversations/{id} | 없음 | 본인 제작 조건·단계·version·latest_script·processing |
| GET /api/me/chats | **conversation_id 필수**, limit=20, offset=0 | 본인 대화방 기록 `{items,limit,offset}`, 최신순. 질문·답변·시각·status·response 포함 |
| POST /api/chat | 아래 새 규격 | 로그인 필요. 저장 성공 후 응답 |
| GET /health | 없음 | 프로세스 상태. 외부 AI·DB 정상 여부 전체를 보증하지 않음 |

## 채팅 흐름

대화방 생성:

```json
{"title":"자취생 아침 메뉴"}
```

상세 응답의 핵심 필드:

```json
{"conversation_id":1,"title":"자취생 아침 메뉴","phase":"briefing","version":0,"brief":{},"latest_script":null,"processing":false}
```

`brief`는 실제 응답에서 Brief의 모든 필드와 null/기본 배열을 포함한다. created_at/updated_at은 UTC ISO 8601 `Z` 문자열이다.

사전 대화 요청:

```json
{"conversation_id":1,"expected_version":0,"action":"message","message":"20대 자취생에게 쉬운 아침 메뉴를 알려주는 30초 릴스를 만들고 싶어요."}
```

정상 응답의 핵심 형태:

```json
{"chat_id":1,"conversation_id":1,"request_id":"server-generated-uuid","version":1,"phase":"briefing","reply_type":"question","answer":"등장 방식과 원하는 분위기를 알려주세요.","brief":{},"missing_fields":["presentation_mode","direction_style","core_message"],"follow_up_questions":[],"script":null,"references":[]}
```

위 답변은 형식 예시이며 실제 AI 동작·결과를 보증하는 샘플이 아니다. follow_up_questions는 실제 응답에서 최대 2개 `{field,question,suggestions}`를 포함한다.

조건이 충분하면 `phase=ready`, `reply_type=brief_summary`, `brief.confirmed=false`로 요약한다. A는 요약을 보여주고 사용자가 확인 버튼을 눌렀을 때 다음 요청을 보낸다.

```json
{"conversation_id":1,"expected_version":2,"action":"generate","message":"이 조건으로 대본을 작성해 주세요."}
```

성공하면 `phase=drafted`, `reply_type=script`, `brief.confirmed=true`이며 `script`에 제목·구조 이유·장면·rationale·저장된 script_id/revision/parent_script_id가 있다. references는 서버가 실제 검색 카드에서 조립한다. rationale은 `{scene_nos,card_ids,explanation}`이다. 장면은 `{scene_no,start_sec,end_sec,purpose,visual,dialogue,caption,direction}`이며 시작 0초부터 목표 길이까지 이어져야 한다.

수정:

```json
{"conversation_id":1,"expected_version":3,"action":"revise","message":"첫 장면의 표현을 더 친근하게 바꿔 주세요.","base_script_id":1}
```

현재 대본 ID와 일치해야 한다. `revision`이 증가하고 부모 대본을 기록한다. 길이·타겟 등 기획 자체를 바꾸려면 `action=message`로 조건을 갱신하고 요약을 다시 확인한다. 설명 질문은 `reply_type=explanation`으로 답할 수 있다. 이전 대본 버전의 별도 목록 API는 초기 범위에 없으며 저장된 대화 response 또는 확인 SQL로 추적한다.

## 내부 저장 규격과 변경 관리

- `begin_turn`: 사용자·대화방·expected_version 검사, 처리 표시·턴 저장, 대화방별 최근 성공 Q/A 5쌍 반환. AI 대기 전에 쓰기 트랜잭션을 끝낸다.
- `complete_turn`: active_request_id·만료·version을 다시 확인하고 조건·답변·대본·출처를 한 트랜잭션으로 저장한다. 버전 +1, 처리 표시 해제.
- `fail_turn`: 실패 상태만 저장하고 이전 성공 기획·대본·version을 유지한다. 늦은 결과는 새 요청을 덮어쓰지 않는다.

사용자·대화방·질문/응답·대본 버전을 분리하여 관리한다. 웹 절은 `locator={type:"html_section",heading:...}`로 기록한다. 웹 도구로 PDF 본문의 위치를 확인한 카드는 `locator={type:"pdf_pages",heading:...,pdf_page_start:10,pdf_page_end:10}`을 사용하며 파일 첫 페이지가 1인 기준이다. references에는 pdf_url, pdf_page_start/end, limitations, application_notes, research_topic_ids가 추가된다. PDF를 열람한 것과 로컬 파일을 확보한 것은 구분하며 바이트 해시는 미확보 상태다. 원문 없는 설명은 확인 불가 안내를 반환한다.

질문 1~6000자, 각 기획 문자열 최대 300자, 길이 10~180초는 제품의 초기 지원 범위다. 인스타그램 공식 길이 제한을 의미하지 않는다. 모델/클라이언트의 임의 confirmed=true는 거절한다. 원본 제작 조건은 최근 Q/A와 별도 저장하므로 대화가 길어져도 유지한다.
