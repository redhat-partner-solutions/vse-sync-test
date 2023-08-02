# This needs access to private git repos, so uses the `--ssh` option of `podman build`.
# e.g. `podman build --ssh=default .`
#
# You must have an SSH key which is authorized for the github account, and that does
# NOT require a password. It must be added to your github account.
#
# If git clone fails with an error like this:
# agent key RSA SHA256:BSM91TfbWaV/8f0dYA6Itp7xd7mxVcCc8Ineu2YK9bc returned incorrect signature type
#
# make sure your SSH key does not require a password.
# I also had to create a key of type ED25519 for it to work, RSA did not work.
# `ssh-keygen -t ed25519`
#


FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

# RUN rpm -ivh https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
RUN microdnf install -y git golang python3 python3-pip tar python3-yaml jq
RUN pip3 install pandas junitparser

ADD https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest/openshift-client-linux.tar.gz /tmp
RUN tar -C /usr/bin -xzf /tmp/openshift-client-linux.tar.gz 

ENV VSE_DIR=/usr/vse
RUN mkdir -p ${VSE_DIR}
WORKDIR ${VSE_DIR}

RUN mkdir -p -m 0600 ~/.ssh && \
    ssh-keyscan -H github.com >> ~/.ssh/known_hosts

RUN --mount=type=ssh git clone --depth=1 git@github.com:redhat-partner-solutions/testdrive.git

RUN --mount=type=ssh git clone --depth=1 git@github.com:redhat-partner-solutions/vse-sync-test.git
WORKDIR ${VSE_DIR}/vse-sync-test
RUN --mount=type=ssh git submodule update --init --recursive

WORKDIR ${VSE_DIR}
RUN --mount=type=ssh git clone git@github.com:redhat-partner-solutions/vse-sync-collection-tools.git
WORKDIR ${VSE_DIR}/vse-sync-collection-tools
RUN go build

WORKDIR ${VSE_DIR}
CMD ["./vse-sync-test/hack/e2e.sh", "-k", "/usr/vse/kubeconfig", "-d", "1500s"]
