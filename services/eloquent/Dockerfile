FROM python:3.5-alpine

#RUN apk add --no-cache python3 && \
#    python3 -m ensurepip && \
#    rm -r /usr/lib/python*/ensurepip && \
#    pip3 install --upgrade pip setuptools && \
#    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
#    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
#    rm -r /root/.cache && \
#    apk --update add redis && \
#    redis-server --daemonize yes
RUN apk --update add redis && \
    redis-server --daemonize yes

COPY requirements.txt /home/eloquent/
WORKDIR /home/eloquent
RUN pip3 install -r requirements.txt

CMD redis-server --daemonize yes && python3 start.py
