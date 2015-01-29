FROM node:latest
MAINTAINER Kacper Kowalik <xarthisius.kk@gmail.com>

# Install base
RUN apt-get update && \
    apt-get install -y curl sudo python-dev python-pip vim supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installs Configuration Synchronization service
RUN pip2 install python-etcd urllib3 supervisor-stdout

# Add and run scripts
ADD configsync.py /configsync.py
ADD run.sh /run.sh
ADD proxy.conf /etc/supervisor/conf.d/proxy.conf
RUN chmod 755 /configsync.py /run.sh

ADD . /srv/configurable-http-proxy
WORKDIR /srv/configurable-http-proxy
RUN npm install -g

# proxy port
EXPOSE 8000

CMD ["supervisord", "-n"]
