FROM ubuntu:18.04

ADD ./docker/sources.list /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y software-properties-common libseccomp-dev \
                       python3 python3-pip gcc g++ wget cmake make unzip && \
    add-apt-repository ppa:openjdk-r/ppa && apt-get update && apt-get install -y openjdk-8-jdk

ADD . /lj

#cd /lj && wget https://github.com/QingdaoU/Judger/archive/newnew.zip && \
#    unzip newnew.zip && rm newnew.zip && cd Judger-newnew && \
#    cmake . && make && make install && \

RUN set -ex && ln -s /usr/bin/python3 /usr/bin/python && cd /lj && pip3 install . pytest -i https://pypi.doubanio.com/simple/ && \
    pytest && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/*
