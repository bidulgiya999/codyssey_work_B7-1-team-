# 비교 대상 소스·README 점검 — 2026-10-21

## 팀원이 다른 README를 본 이유

팀 저장소 origin은 bidulgiya999/codyssey_work_B7-1-team-가 맞다. 그러나 GitHub 기본 브랜치 main과 develop은 초기 가져오기 커밋 87b92d5에 있고, 인스타 릴스 제작 코치는 feature/c-ai-deploy에서 작성됐다. 저장소의 루트 URL은 main의 예전 README를 표시하므로 다른 팀의 소개와 배포 링크가 보였다.

팀에서 실행할 코드는 [현재 구현 브랜치](https://github.com/bidulgiya999/codyssey_work_B7-1-team-/tree/feature/c-ai-deploy)다. 최신 구현의 원격 반영·검토 후 develop → main으로 PR 통합해야 루트 링크의 코드와 README가 함께 교체된다. 문서만 바꾸고 예전 코드를 우리 코드라고 안내하지 않는다.

## 재작성 범위

- 계정 입력 스키마 → 계정 서비스 → 인증 라우터를 분리했다.
- 새 scrypt 비밀번호 저장과 기존 계정의 성공 로그인 시 업그레이드를 구현했다.
- 세션 ID 검증·DB 연결·계정 모델·브라우저 인증/API 클라이언트를 재구현했다.
- B의 대화방·기록 API와 C의 AI 채팅 API를 분리했다.
- 사전 기획·템플릿 선택·자료 검색·장면별 대본/근거·검증/버전/실패 복구는 현재 서비스의 요구로 작성했다.
- 앱·화면·프롬프트·기획·역할 문서를 인스타 릴스 제작 코치로 구성했다. 팀원은 A 이송하, B 김시현, C 황승재다.

## 읽기 전용 비교

    .venv/Scripts/python.exe scripts/audit_reference.py
    .venv/Scripts/python.exe scripts/audit_reference.py --ref upstream/main

| 비교 기준 | 원본 app 파일 | 현재 앱 소스 파일 | 동일 비자명 파일 | 전체 Python AST 동일 |
|---|---:|---:|---:|---:|
| 가져온 develop e7b34807e384e802851f916332340b2f311b2941 | 35 | 31 | 0 | 0 |
| 확인한 main d55938ad3c27a48a3b0b8705a605871146c02be9 | 35 | 31 | 0 | 0 |

비교 스크립트는 앱의 Python·JS·CSS·HTML 전체 파일의 일치와 Python AST 일치를 확인한다. 80바이트 미만 파일과 구현 없는 초기화 모듈은 실질적 구현으로 세지 않는다. 데이터·문서·코드 조각 유사도 전체를 증명하는 도구는 아니다. FastAPI·SQLAlchemy API·과제 필수 기능의 공통성이나 모든 공통 문자열을 제거했다고 주장하지 않는다.

원본을 가져온 과거 사실과 참조 기록은 [재작성 이력](UPSTREAM.md)에 보존한다. 원본 팀의 저자·커밋·운영 URL을 현재 팀의 실적으로 사용하지 않는다. 기존 사용자 데이터의 ID·물리 테이블 보존은 호환성 목적이며 서버 키·DB 파일은 Git에 넣지 않는다.
