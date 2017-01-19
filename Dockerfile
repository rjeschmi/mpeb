FROM rjeschmi/easybuild-centos7:3.0.0

MAINTAINER Robert Schmidt <rjeschmi@gmail.com>
USER root
ADD ./dist/*.gz /build/mpeb

WORKDIR /build/mpeb
RUN cd Monkey* && python setup.py install

ADD docker_build/mpeb.sh /usr/bin/mpeb.sh
RUN chmod a+x /usr/bin/mpeb.sh
USER easybuild


ENTRYPOINT ["/usr/bin/mpeb.sh"]

