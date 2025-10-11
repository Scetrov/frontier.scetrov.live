# See https://containers.dev/ for devcontainer docs
FROM mcr.microsoft.com/devcontainers/javascript-node:20

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    hugo \
    git \
    python3 \
    python3-pip \
    make \
    curl \
    wget \
    ca-certificates \
    gnupg \
 && rm -rf /var/lib/apt/lists/*

# Install python pre-commit system-wide
RUN python3 -m pip install --upgrade pip pre-commit

# Install markdownlint-cli globally so npx works reliably in container
RUN npm install -g markdownlint-cli

# Create a non-root workspace user if the base image did not provide one
ARG USERNAME=node
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN if id -u ${USERNAME} >/dev/null 2>&1; then echo "user exists"; else \
      groupadd --gid $USER_GID $USERNAME || true && \
      useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME ; \
    fi

WORKDIR /workspace

CMD ["sleep", "infinity"]
