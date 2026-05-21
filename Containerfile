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

# Build from the parent directory that contains all three repos, e.g.:
#   podman build -f vse-sync-test/Containerfile -t localhost/boundary:latest .
COPY vse-sync-test-report/ ${VSE_DIR}/vse-sync-test-report/
COPY vse-sync-test/ ${VSE_DIR}/vse-sync-test/
COPY vse-sync-collection-tools/ ${VSE_DIR}/vse-sync-collection-tools/
WORKDIR ${VSE_DIR}/vse-sync-collection-tools
RUN go mod vendor

WORKDIR ${VSE_DIR}
# GNRD defaults: log demux, no DPLL netlink collector, full plots in PDF (no PDF timeout).
ENV VSE_DEMUX_DPLL_FROM_LOG=1
ENV GNRD_SKIP_DPLL_COLLECTOR=1
ENV E2E_SKIP_PLOTS=0
ENV E2E_SKIP_WANDER_PLOTS=0
ENV E2E_PDF_TIMEOUT_SEC=0
CMD ["./vse-sync-test/cmd/e2e.sh", "-d", "2000s", "/usr/vse/kubeconfig"]
