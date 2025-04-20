FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV FLINK_VERSION=1.20.0
ENV SCALA_VERSION=2.12
ENV FLINK_HOME=/usr/local/flink
ENV VENV_PATH=/root/venvs/flink
ENV PYTHON_VERSION=3.10

# 1. 필수 패키지 설치 및 Python 3.10 PPA 등록
RUN apt-get update && \
    apt-get install -y \
        wget \
        curl \
        git \
        netcat \
        software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    apt-get install -y \
        openjdk-8-jdk \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-distutils \
        python3-pip \
        unzip && \
    apt-get clean

# 2. JAVA_HOME 동적 설정 (아키텍처에 상관없이 자동 감지)
RUN echo 'export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))' >> /etc/profile && \
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile

# 3. Flink 다운로드 및 설치
RUN wget https://archive.apache.org/dist/flink/flink-${FLINK_VERSION}/flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz && \
    tar -xvzf flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz && \
    mv flink-${FLINK_VERSION} ${FLINK_HOME} && \
    rm flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz

# 4. requirements.txt 복사
COPY requirements.txt ./

# 5. PyFlink 가상환경 구성 및 설치 (requirements.txt 사용)
RUN python${PYTHON_VERSION} -m venv ${VENV_PATH} && \
    JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac)))) && \
    PATH=$JAVA_HOME/bin:$PATH && \
    export JAVA_HOME && export PATH && \
    ${VENV_PATH}/bin/pip install --upgrade pip setuptools wheel && \
    ${VENV_PATH}/bin/pip install apache-flink==${FLINK_VERSION} && \
    ${VENV_PATH}/bin/pip install -r requirements.txt

# 6. PyFlink 로그 디렉토리 권한 설정
RUN mkdir -p ${VENV_PATH}/lib/python${PYTHON_VERSION}/site-packages/pyflink/log && \
    chmod -R 777 ${VENV_PATH}/lib/python${PYTHON_VERSION}/site-packages/pyflink/log

# 7. Flink 설정 복사
COPY services/flink/flink-conf.yaml ${FLINK_HOME}/conf/flink-conf.yaml

# 8. 환경변수 등록 및 가상환경 활성화 설정
RUN echo "export FLINK_HOME=${FLINK_HOME}" >> /etc/profile && \
    echo "export PYFLINK_PYTHON=${VENV_PATH}/bin/python" >> /etc/profile && \
    # 가상환경을 자동으로 활성화하도록 설정
    echo "source ${VENV_PATH}/bin/activate" >> ~/.bashrc

# 9. 가상환경의 bin 디렉토리를 PATH에 추가
ENV PATH="${VENV_PATH}/bin:${FLINK_HOME}/bin:$PATH"

# 10. 클러스터는 수동으로 띄울 수 있게 bash만 유지
CMD ["/bin/bash"]