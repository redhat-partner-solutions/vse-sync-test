FROM registry.access.redhat.com/ubi9/ubi-minimal:latest
#node name should be passed in when testing an MNO cluster defaulting to SNO usecase of empty.
ENV PTPNODENAME=""
RUN microdnf install -y git golang python3 python3-pip tar python3-yaml jq ruby
RUN pip3 install pandas junitparser matplotlib allantools
RUN gem install asciidoctor-pdf:2.3.19 asciidoctor-diagram:2.3.2 rouge:4.5.1

ADD https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest/openshift-client-linux.tar.gz /tmp
RUN tar -C /usr/bin -xzf /tmp/openshift-client-linux.tar.gz

ENV VSE_DIR=/usr/vse
RUN mkdir -p ${VSE_DIR}
WORKDIR ${VSE_DIR}

RUN git clone -v --depth=1 https://github.com/redhat-partner-solutions/vse-sync-test-report.git

RUN git clone -v --depth=1 https://github.com/redhat-partner-solutions/vse-sync-test.git

RUN git clone -v https://github.com/redhat-partner-solutions/vse-sync-collection-tools.git
WORKDIR ${VSE_DIR}/vse-sync-collection-tools
RUN go mod vendor

WORKDIR ${VSE_DIR}
CMD ["./vse-sync-test/cmd/e2e.sh", "-d", "2000s", "/usr/vse/kubeconfig"]
