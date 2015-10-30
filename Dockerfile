FROM mhart/alpine-node:latest
MAINTAINER Kieran David Evans <keyz182@gmail.com>

RUN apk --progress add --update supervisor musl python3 python3-dev build-base curl \
  && pip3 install --upgrade pip \
  && pip3 install python-etcd urllib3 supervisor-stdout \
  && apk --progress del --purge --rdepends python3-dev build-base \
  && rm -rf /var/cache/apk/*


# Add and run scripts
ADD configsync.py /configsync.py
ADD run.sh /run.sh
RUN mkdir -p /etc/supervisor/conf.d/
ADD proxy.conf /etc/supervisor/conf.d/proxy.conf
ADD ./supervisord.conf /etc/supervisor/supervisord.conf
RUN chmod 755 /configsync.py /run.sh

ADD . /srv/configurable-http-proxy
WORKDIR /srv/configurable-http-proxy
RUN npm install -g

# proxy port
EXPOSE 8000

CMD ["supervisord", "-n"]
