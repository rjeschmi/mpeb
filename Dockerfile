FROM rjeschmi/easybuild-centos7

MAINTAINER Robert Schmidt <rjeschmi@gmail.com>
USER root
ADD . /build/mpeb

WORKDIR /build/mpeb
RUN python setup.py install
