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

# Pin branches that include GNRD ts2phc detect fixes (override at build time if needed).
ARG VSE_SYNC_TEST_REPORT_REPO=https://github.com/redhat-partner-solutions/vse-sync-test-report.git
ARG VSE_SYNC_TEST_REPO=https://github.com/redhat-partner-solutions/vse-sync-test.git
ARG VSE_SYNC_TEST_REF=newvsevarun
ARG VSE_COLLECTION_TOOLS_REPO=https://github.com/v72singh/vse-sync-collection-tools.git
ARG VSE_COLLECTION_TOOLS_REF=varuncollector-tool

RUN git clone -v --depth=1 ${VSE_SYNC_TEST_REPORT_REPO}
RUN git clone -v --depth=1 -b ${VSE_SYNC_TEST_REF} ${VSE_SYNC_TEST_REPO}
RUN git clone -v --depth=1 -b ${VSE_COLLECTION_TOOLS_REF} ${VSE_COLLECTION_TOOLS_REPO}
WORKDIR ${VSE_DIR}/vse-sync-collection-tools
RUN go mod vendor

WORKDIR ${VSE_DIR}
CMD ["./vse-sync-test/cmd/e2e.sh", "-d", "2000s", "/usr/vse/kubeconfig"]
