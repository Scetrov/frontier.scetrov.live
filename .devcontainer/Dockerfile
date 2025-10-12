# Use the same base image that was previously specified in devcontainer.json
FROM mcr.microsoft.com/devcontainers/go:1-1.24-bookworm

# Install Node.js 24 (LTS) via NodeSource
RUN apt-get update && apt-get install -y curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    npm install -g markdownlint-cli

# Create GPG configuration files
RUN mkdir -p /home/vscode/.gnupg && \
    echo "enable-ssh-support" > /home/vscode/.gnupg/gpg-agent.conf && \
    echo "allow-loopback-pinentry" >> /home/vscode/.gnupg/gpg-agent.conf && \
    echo "use-agent" > /home/vscode/.gnupg/gpg.conf && \
    echo "pinentry-mode loopback" >> /home/vscode/.gnupg/gpg.conf && \
    chown -R vscode:vscode /home/vscode/.gnupg && \
    chmod 700 /home/vscode/.gnupg && \
    chmod 600 /home/vscode/.gnupg/gpg-agent.conf && \
    chmod 600 /home/vscode/.gnupg/gpg.conf

RUN chown -R vscode:vscode /home/vscode/.gnupg
