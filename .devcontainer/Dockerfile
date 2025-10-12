# Use the same base image that was previously specified in devcontainer.json
FROM mcr.microsoft.com/devcontainers/go:1-1.24-bookworm

# Install Node.js 24 (LTS) via NodeSource
RUN apt-get update && apt-get install -y curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    npm install -g markdownlint-cli

RUN chown -R vscode:vscode /home/vscode/.gnupg
