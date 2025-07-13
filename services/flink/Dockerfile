FROM apache/flink:1.20.0-scala_2.12-java11

ENV DEBIAN_FRONTEND=noninteractive
# FLINK_VERSION과 SCALA_VERSION은 FROM에서 이미 설정되어 있을 수 있으나,
# 명시적으로 다시 설정하여 다른 곳에서 참조할 때 일관성을 유지할 수 있습니다.
ENV FLINK_VERSION=1.20.0
ENV SCALA_VERSION=2.12
# 공식 이미지의 Flink 설치 경로에 맞춤
ENV FLINK_HOME=/opt/flink
ENV VENV_PATH=/root/venvs/flink
# 공식 이미지에 설치된 Python 버전 확인 후 필요시 조정
ENV PYTHON_VERSION=3.10 

# 1. 필수 패키지 설치 및 Python 3.10 PPA 등록 (필요한 경우)
# apache/flink 이미지에 따라 python3 및 관련 패키지가 이미 설치되어 있을 수 있습니다.
# 만약 python3.10이 없거나 필요한 다른 패키지가 있다면 추가합니다.
RUN apt-get update && \
    apt-get install -y \
        wget \
        curl \
        git \
        netcat \
        software-properties-common && \
    # 공식 이미지에 Python 3.10이 기본으로 없으면 PPA를 추가하여 설치합니다.
    # 일반적으로 Flink 이미지는 Python2/3 중 하나를 포함하며,
    # 정확한 Python 버전을 원한다면 PPA를 통한 설치가 필요할 수 있습니다.
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    apt-get install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-distutils \
        python3-pip \
        unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. JAVA_HOME 동적 설정 (공식 이미지에서 이미 설정되어 있으므로 필요 없음. Flink_HOME도 마찬가지)
# 하지만 다른 스크립트에서 JAVA_HOME을 참조할 경우를 대비하여 /etc/profile에 추가하는 것은 유지할 수 있습니다.
# RUN echo 'export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))' >> /etc/profile && \
#     echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile

# 3. Flink 다운로드 및 설치 (공식 이미지에서 이미 설치되어 있으므로 제거)
# RUN wget ...

# 4. requirements.txt 복사
COPY ./services/flink/requirements.txt ./

# 5. PyFlink 가상환경 구성 및 설치 (requirements.txt 사용)
# 공식 이미지의 Flink 설치 경로에 맞춰 JAVA_HOME 경로 설정이 필요 없을 수 있음.
# JAVA_HOME은 공식 이미지 내부에서 이미 설정되어 있을 가능성이 높습니다.
RUN python${PYTHON_VERSION} -m venv ${VENV_PATH} && \
    # 공식 Flink 이미지의 JAVA_HOME을 사용하거나,
    # 이미 PATH에 포함되어 있어 명시적으로 설정할 필요 없을 수 있습니다.
    # 만약 pyflink 설치 시 JAVA_HOME을 명시적으로 요구한다면 주석 해제.
    # export JAVA_HOME=/opt/java/openjdk && \ # 또는 Flink 이미지의 실제 JAVA_HOME 경로
    # export PATH=$JAVA_HOME/bin:$PATH && \
    ${VENV_PATH}/bin/pip install --upgrade pip setuptools wheel && \
    ${VENV_PATH}/bin/pip install apache-flink==${FLINK_VERSION} && \
    ${VENV_PATH}/bin/pip install -r requirements.txt && \
    # 가상환경 디렉토리에 대한 권한을 설정하여 flink 사용자가 접근할 수 있도록 함
    chmod -R 755 /root && \
    chmod -R 755 ${VENV_PATH} && \
    # Python 실행 파일에 실행 권한 부여
    chmod 755 ${VENV_PATH}/bin/python

# 6. PyFlink 로그 디렉토리 권한 설정
# VENV_PATH 하위에 직접 생성하는 것이 일반적
RUN mkdir -p ${VENV_PATH}/lib/python${PYTHON_VERSION}/site-packages/pyflink/log && \
    chmod -R 777 ${VENV_PATH}/lib/python${PYTHON_VERSION}/site-packages/pyflink/log

COPY ./services/flink/config/flink-sql-connector-kafka-3.3.0-1.20.jar ${FLINK_HOME}/lib/
# 7. Flink 설정 복사
# 공식 이미지의 Flink conf 디렉토리는 보통 /opt/flink/conf 입니다.
COPY ./services/flink/flink-conf.yaml ${FLINK_HOME}/conf/flink-conf.yaml

# 8. 환경변수 등록 및 가상환경 활성화 설정
# 공식 이미지의 FLINK_HOME 경로에 맞춰 조정
RUN echo "export FLINK_HOME=${FLINK_HOME}" >> /etc/profile && \
    echo "export PYFLINK_PYTHON=${VENV_PATH}/bin/python" >> /etc/profile && \
    # 가상환경을 자동으로 활성화하도록 설정
    echo "source ${VENV_PATH}/bin/activate" >> ~/.bashrc

# 9. 가상환경의 bin 디렉토리를 PATH에 추가
# 공식 이미지의 Flink bin 디렉토리는 보통 /opt/flink/bin 입니다.
ENV PATH="${VENV_PATH}/bin:${FLINK_HOME}/bin:$PATH"

# 10. 클러스터는 수동으로 띄울 수 있게 bash만 유지
CMD ["/bin/bash"]