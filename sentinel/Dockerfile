ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt

COPY . /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
