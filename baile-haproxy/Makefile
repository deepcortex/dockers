OWNER=deepcortex
IMAGE_NAME=baile-haproxy
VCS_REF=`git rev-parse --short HEAD`
IMAGE_VERSION=1.0.$(TRAVIS_BUILD_NUMBER)
BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"`
QNAME=$(OWNER)/$(IMAGE_NAME)

GIT_TAG=$(QNAME):$(VCS_REF)
BUILD_TAG=$(QNAME):$(IMAGE_VERSION)
LATEST_TAG=$(QNAME):latest

default: build tag

debug:
	docker run --rm -it $(LATEST_TAG) /bin/bash

test:
	docker run -e S3_BUCKET="dev.deepcortex.ai.s3.amazonaws.com" \
		-e BAILE_API_PATH="baile" \
		-e SQL_SERVER_API_PATH="sql" \
		-e REMOTE_JOB_GW_PATH="remote" \
		-e BAILE_ADDRESS="127.0.0.1:1111" \
		-e SQL_SERVER_ADDRESS="127.0.0.1:1112" \
		-e REMOTE_JOB_GW_ADDRESS="127.0.0.1:1113" \
		-e VPC_DNS="127.0.0.1" \
		-e DNS_RESOLVER="google" \
		--rm -it $(LATEST_TAG) \
		haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg

run:
	docker run --rm -it $(LATEST_TAG) R

lint:
	docker run -it --rm -v "$(PWD)/Dockerfile:/Dockerfile:ro" redcoolbeans/dockerlint

build:
	docker build \
		--build-arg VCS_REF=$(VCS_REF) \
		--build-arg IMAGE_VERSION=$(IMAGE_VERSION) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		-t $(GIT_TAG) .

tag:
	docker tag $(GIT_TAG) $(BUILD_TAG)
	docker tag $(GIT_TAG) $(LATEST_TAG)

push:
	docker push $(GIT_TAG)
	docker push $(BUILD_TAG)
	docker push $(LATEST_TAG)

pre-release: lint build tag test

release: pre-release push
