FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. 필수 시스템 도구 및 Java 설치
RUN apt-get update && \
    apt-get install -y \
        openjdk-11-jdk \
        curl \
        wget \
        net-tools \
        iputils-ping \
        dnsutils \
        vim \
        lsof \
        netcat \
        unzip \
        tar \
        git \
        python3 \
        python3-pip \
        python3-venv && \
    apt-get clean

# 2. JAVA_HOME 동적 설정 (아키텍처에 상관없이 자동 감지)
RUN echo 'export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))' >> /etc/profile && \
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile

# 3. Kafka 다운로드 및 설치
RUN wget https://dlcdn.apache.org/kafka/3.9.0/kafka_2.12-3.9.0.tgz && \
    tar -xzf kafka_2.12-3.9.0.tgz && \
    mv kafka_2.12-3.9.0 /usr/local/kafka && \
    rm kafka_2.12-3.9.0.tgz

# 4. Kafka 설정 파일 내 zookeeper 주소 수정 (localhost → zookeeper)
RUN sed -i 's|localhost:2181|zookeeper:2181|' /usr/local/kafka/config/server.properties

# 5. Python 가상환경 설정 및 필요한 패키지 설치
COPY requirements.txt /tmp/
RUN python3 -m venv /opt/venv && \
    JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac)))) && \
    PATH=$JAVA_HOME/bin:$PATH && \
    export JAVA_HOME && export PATH && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r /tmp/requirements.txt

# 6. 가상환경 활성화 설정
RUN echo 'source /opt/venv/bin/activate' >> ~/.bashrc

# 7. Kafka 환경 변수 등록
ENV KAFKA_HOME=/usr/local/kafka
ENV PATH="$KAFKA_HOME/bin:/opt/venv/bin:$PATH"

# 8. Kafka 서버용 포트 개방
EXPOSE 9092

# 9. Kafka 브로커 실행
CMD ["kafka-server-start.sh", "/usr/local/kafka/config/server.properties"]
