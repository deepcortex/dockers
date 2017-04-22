FROM rabbitmq:3.6.9-management-alpine

ENV RABBITMQ_ERLANG_COOKIE= \
  RABBITMQ_DEFAULT_USER=guest \
  RABBITMQ_DEFAULT_PASS=guest \
  RABBITMQ_DEFAULT_VHOST=/ \
  RABBITMQ_NODE_PORT=5672 \
  RABBITMQ_DIST_PORT=25672 \
  RABBITMQ_NET_TICKTIME=60 \
  RABBITMQ_CLUSTER_PARTITION_HANDLING=ignore \
  ERL_EPMD_PORT=4369 \
  RABBITMQ_HIPE_COMPILE=1 \
  RABBITMQ_MANAGEMENT_PORT=15672 \
  MARATHON_URI=http://marathon.mesos:8080

RUN (cd /tmp && apk add --no-cache python3 && pip3 install --upgrade pip requests && rm -rf /var/lib/rabbitmq/.cache)

ADD ./rabbitmq-cluster.py /rabbitmq-cluster.py

RUN chmod +x /rabbitmq-cluster.py

CMD "/rabbitmq-cluster.py"

LABEL maintainer="aldrin+gh@leal.eng.br" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="DeepCortex" \
      org.label-schema.description="DeepCortex is the world’s first cloud based, automated platform for doing the entire end-to-end Data Science process" \
      org.label-schema.url="http://www.deepcortex.com/" \
      org.label-schema.vcs-ref=$VCS_REF \
	  org.label-schema.version=$IMAGE_VERSION \
      org.label-schema.vcs-url="https://github.com/deepcortex/dockers" \
      org.label-schema.vendor="DeepCortex" \
      org.label-schema.schema-version="1.0" \
	  org.label-schema.docker.cmd="docker run --rm -it -v HOST_PATH:/projects deepcortex/dcos-rabbitmq /bin/sh"
