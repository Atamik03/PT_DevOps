FROM postgres:latest

ARG DB_REPL_PASSWORD
ARG DB_REPL_USER
ARG DB_DATABASE

ENV LANG=ru_RU.utf8
ENV LANGUAGE=ru_RU:ru
ENV LC_ALL=ru_RU.utf8

RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.utf8


COPY init.sql /docker-entrypoint-initdb.d/

RUN apt update && apt install sed && apt install postgresql-client

RUN sed -i "s/%REPLUSER_PASSWORD%/$DB_REPL_PASSWORD/g" /docker-entrypoint-initdb.d/init.sql
RUN sed -i "s/%DB_REPL_USER%/$DB_REPL_USER/g" /docker-entrypoint-initdb.d/init.sql
RUN sed -i "s/%DBNAME%/$DB_DATABASE/g" /docker-entrypoint-initdb.d/init.sql

RUN mkdir -p /oracle/pg_data/archive/ && chown -R postgres:postgres /oracle/pg_data/archive/

RUN echo "listen_addresses = '*'" >> /usr/share/postgresql/postgresql.conf.sample