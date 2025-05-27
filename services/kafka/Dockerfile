# Apache Kafka 공식 이미지 기반
FROM bitnami/kafka:3.9.0

# root 권한으로 작업
USER root

# 1. 패키지 리스트 업데이트 및 사용 가능한 패키지 확인
RUN apt-get update && \
    apt-cache search netcat

# 2. 필수 시스템 도구 설치
RUN apt-get install -y \
        curl \
        wget \
        net-tools \
        iputils-ping \
        dnsutils \
        vim \
        lsof \
        netcat-traditional \
        unzip \
        tar \
        git \
        python3 \
        python3-pip \
        python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 생성
RUN mkdir -p /opt/workspace

# 4. Python 가상환경 설정 및 필요한 패키지 설치
COPY ./services/kafka/requirements.txt /tmp/
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r /tmp/requirements.txt

# 5. 환경 변수 설정
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/opt/workspace:$PYTHONPATH"

# 6. 간단한 시작 스크립트 작성
RUN echo '#!/bin/bash' > /opt/start-kafka.sh && \
    echo 'source /opt/venv/bin/activate' >> /opt/start-kafka.sh && \
    echo 'exec /opt/bitnami/scripts/kafka/entrypoint.sh /opt/bitnami/scripts/kafka/run.sh' >> /opt/start-kafka.sh && \
    chmod +x /opt/start-kafka.sh

# 7. Kafka 서버용 포트 개방
EXPOSE 9092

# 8. 작업 디렉토리 설정
WORKDIR /opt/workspace

# 9. Kafka 브로커 실행
CMD ["/opt/start-kafka.sh"]