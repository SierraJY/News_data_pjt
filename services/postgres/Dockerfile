FROM postgres:16

RUN apt-get update && \
    apt-get install -y git postgresql-server-dev-16 make gcc && \
    git clone https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    rm -rf pgvector

COPY init.sql /docker-entrypoint-initdb.d/
COPY pg_hba.conf /etc/postgresql/pg_hba.conf
# 아래 설정은 PostgreSQL이 커스텀 pg_hba.conf를 사용하게 하기 위함
CMD ["postgres", "-c", "hba_file=/etc/postgresql/pg_hba.conf"]
