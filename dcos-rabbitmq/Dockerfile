FROM rabbitmq:3.6.9-management-alpine

ARG BUILD_DATE
ARG IMAGE_VERSION
ARG VCS_REF

RUN apk add --no-cache python3 && pip3 install --upgrade pip requests

ENV RABBITMQ_ERLANG_COOKIE=randomsting
ENV RABBITMQ_DEFAULT_USER=guest
ENV RABBITMQ_DEFAULT_PASS=guest
ENV RABBITMQ_DEFAULT_VHOST=/
ENV RABBITMQ_NODE_PORT=5672
ENV RABBITMQ_DIST_PORT=25672
ENV RABBITMQ_NET_TICKTIME=60
ENV RABBITMQ_CLUSTER_PARTITION_HANDLING=ignore
ENV ERL_EPMD_PORT=4369
ENV RABBITMQ_HIPE_COMPILE=1
ENV RABBITMQ_MANAGEMENT_PORT=15672
ENV MARATHON_URI=http://marathon.mesos:8080

WORKDIR /

RUN echo BUILD_DATE=$(BUILD_DATE) > .meta
RUN echo IMAGE_VERSION=$(IMAGE_VERSION) >> .meta
RUN echo VCS_REF=$(VCS_REF) >> .meta

RUN rm -rf /var/lib/rabbitmq/.cache

COPY ./rabbitmq-cluster.py /rabbitmq-cluster.py

CMD [ "/usr/bin/python3", "rabbitmq-cluster.py" ]

LABEL maintainer="aldrin+gh@leal.eng.br"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.name="DeepCortex"
LABEL org.label-schema.description="DeepCortex is the world’s first cloud based, automated platform for doing the entire end-to-end Data Science process"
LABEL org.label-schema.url="http://www.deepcortex.com/"
LABEL org.label-schema.vcs-ref=$VCS_REF
LABEL org.label-schema.version=$IMAGE_VERSION
LABEL org.label-schema.vcs-url="https://github.com/deepcortex/dockers"
LABEL org.label-schema.vendor="DeepCortex"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.docker.cmd="docker run --rm -it -v HOST_PATH:/projects deepcortex/dcos-rabbitmq /bin/sh"
