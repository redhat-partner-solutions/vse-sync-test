# Image for T-GM / BC sync testing.
#
# Build from a directory that contains BOTH local repos (with your detect fixes):
#   ./vse-sync-collection-tools/
#   ./vse-sync-test/
#
#   cd /path/to/parent
#   podman build --no-cache -f vse-sync-test/Containerfile -t localhost/boundary:latest .
#
# Or use:  ./vse-sync-test/cmd/build-image.sh /path/to/parent
#
# vse-sync-test-report is cloned from GitHub (PDF templates only; not needed for detect).

FROM registry.access.redhat.com/ubi9/ubi-minimal:latest
ENV PTPNODENAME=""
RUN microdnf install -y git golang python3 python3-pip tar python3-yaml jq ruby
RUN pip3 install pandas junitparser matplotlib allantools
RUN gem install asciidoctor-pdf:2.3.19 asciidoctor-diagram:2.3.2 rouge:4.5.1

ADD https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest/openshift-client-linux.tar.gz /tmp
RUN tar -C /usr/bin -xzf /tmp/openshift-client-linux.tar.gz

ENV VSE_DIR=/usr/vse
RUN mkdir -p ${VSE_DIR}
WORKDIR ${VSE_DIR}

# PDF/report templates (upstream is fine; avoids requiring a third local checkout).
RUN git clone -v --depth=1 https://github.com/redhat-partner-solutions/vse-sync-test-report.git

# Your branches with detect / e2e / parser fixes — must be in the build context.
COPY vse-sync-test/ ${VSE_DIR}/vse-sync-test/
COPY vse-sync-collection-tools/ ${VSE_DIR}/vse-sync-collection-tools/

WORKDIR ${VSE_DIR}/vse-sync-collection-tools
RUN go mod vendor

WORKDIR ${VSE_DIR}
CMD ["./vse-sync-test/cmd/e2e.sh", "-d", "2000s", "/usr/vse/kubeconfig"]
