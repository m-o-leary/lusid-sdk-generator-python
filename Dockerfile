FROM rust:latest as rust

RUN cargo install just

FROM openapitools/openapi-generator-cli:latest-release as maven

RUN apt update && apt -y install jq git
# need to install the following fo python
RUN apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
RUN apt install -y python3 python3-distutils
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY --from=rust /usr/local/cargo/bin/just /usr/bin/just

RUN mkdir -p /usr/src/
WORKDIR /usr/src/

ENTRYPOINT [ "/bin/bash" ]

# Make ssh dir
# Create known_hosts
# Add github key
RUN mkdir /root/.ssh/ \
    && touch /root/.ssh/known_hosts \
    && ssh-keyscan github.com >> /root/.ssh/known_hosts

RUN --mount=type=ssh \
    git clone git@github.com:finbourne/lusid-sdk-doc-templates.git /tmp/docs \
    && git clone git@github.com:finbourne/lusid-sdk-workflow-template.git /tmp/workflows

COPY generate/ /usr/src/generate
COPY ./justfile /usr/src/