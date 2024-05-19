FROM postgres:latest

ENV LANG=ru_RU.utf8
ENV LANGUAGE=ru_RU:ru
ENV LC_ALL=ru_RU.utf8

RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.utf8


RUN rm -rf /var/lib/postgresql/data/*