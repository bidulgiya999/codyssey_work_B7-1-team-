# Linux 배포 초안

서버 생성·도메인·외부 접속 검증은 수행하지 않았다. 아래는 실행 절차이며 배포 완료 증거가 아니다.

1. Python 3.12·Git·Caddy가 준비된 Linux 서버의 `/srv/reels-coach`에 프로젝트를 체크아웃한다. 서비스 사용자 예시는 ubuntu다. 실제 사용자·경로에 맞게 service 파일을 바꾼다.

```bash
cd /srv/reels-coach
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

2. `/srv/reels-coach-data` 등 영속 DB 디렉터리를 서비스 사용자가 쓸 수 있게 준비한다. `.env`의 SECRET_KEY, GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL을 설정한다. `DATABASE_URL=sqlite:////srv/reels-coach-data/app.db`, `SESSION_HTTPS_ONLY=true`, `ENABLE_API_DOCS=false`를 사용한다. 기존 .env가 있다면 덮어쓰지 않는다.
3. 경로·사용자를 검토하고 service를 등록한다.

```bash
sudo cp deploy/reels-coach.service /etc/systemd/system/reels-coach.service
sudo systemctl daemon-reload
sudo systemctl enable --now reels-coach
sudo systemctl status reels-coach
journalctl -u reels-coach --since '10 minutes ago'
```

4. 앱은 127.0.0.1:8000에 바인딩한다. `deploy/Caddyfile.reels`의 도메인을 실제 도메인으로 변경해 Caddy에 적용한다. DNS가 서버를 가리키고 80/443이 열려 있어야 한다. 인증서·방화벽 작업은 실제 서버 환경을 확인해 수행한다.
5. 외부 네트워크에서 HTTPS 가입·로그인·사전 대화·실제 AI 생성·수정·로그 조회를 확인한다. 키 누락·timeout·공급자 오류 후에도 프로세스가 유지되는지, 재시작 후 DB가 남는지 확인한다.
6. 실제 서비스 URL·확인 시각·검증 결과를 README에 기록한다. GitHub Repository URL은 서비스 URL을 대신하지 않는다.

워커 1개는 초기 운영 설정이며 동시 요청 안전성은 DB 버전·lease 검사에 의존한다. DB를 임시 컨테이너 파일시스템에 두지 않는다. 서버 생성이나 유료 API 호출은 이번 작업에서 수행하지 않았다.
