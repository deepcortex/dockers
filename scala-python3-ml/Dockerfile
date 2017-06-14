FROM deepcortex/scala-python3:latest

RUN conda install numpy=1.12.1 scipy=0.19.0 h5py=2.7 keras=2.0 tensorflow=1.1.0 scikit-learn pandas && \  
    conda clean -tipsy

ARG BUILD_DATE
ARG VCS_REF
ARG IMAGE_VERSION

LABEL maintainer="nsemichev@gmail.com" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="DeepCortex" \
      org.label-schema.description="DeepCortex is the world’s first cloud based, automated platform for doing the entire end-to-end Data Science process" \
      org.label-schema.url="http://www.deepcortex.ai" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.version=$IMAGE_VERSION \
      org.label-schema.vcs-url="https://github.com/deepcortex/dockers" \
      org.label-schema.vendor="DeepCortex" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.docker.cmd="docker run --rm -it deepcortex/scala-python3-ml python"

      
