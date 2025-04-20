# 🚀 Flink 컨테이너 사용 가이드

- Flink 컨테이너는 이미 Dockerfile에서 모든 설정이 완료되어 있음  
- 아래 명령어만 입력하면 클러스터를 바로 시작할 수 있음:

```bash
source /root/venvs/flink/bin/activate
$FLINK_HOME/bin/start-cluster.sh
```

---

# 🧪 Flink 컨테이너 테스트

## 📌 터미널 1 – 입력용 서버 열기
- 입력 데이터를 Flink에게 스트리밍으로 줄 준비

```bash
nc -l 8000
```

- 다음 내용 입력
```
hello world
hello flink
flink flink
```

## 📌 터미널 2 – 예제 실행
- Flink에게 “8000 포트에서 단어를 읽어서 집계해”라고 명령

```bash
$FLINK_HOME/bin/flink run $FLINK_HOME/examples/streaming/SocketWindowWordCount.jar --hostname localhost --port 8000
```

## 📌 웹 UI / 로그로 결과 확인

- 웹 UI 접속: [http://localhost:8081](http://localhost:8081)  
  → 실시간 실행 로그 및 잡 상태 확인 가능

- 또는 컨테이너 내부에서 직접 로그 확인:

```bash
cd $FLINK_HOME
tail -f log/flink-*.out
```
