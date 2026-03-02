# Use the same base image that was previously specified in devcontainer.json
FROM mcr.microsoft.com/devcontainers/go:1.25-trixie

# Install Node.js 24 (LTS) via NodeSource (use GPG-signed repo instead of piping)
RUN apt-get update && apt-get install -y curl ca-certificates gnupg && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_24.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y nodejs && \
    npm install -g npm@latest && \
    npm install -g markdownlint-cli

# Instll prerequisites for pre-commit hooks
RUN apt-get update && apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libxss1 libxshmfence1 \
    pre-commit

# Install htmltest (link checker) so pre-commit hooks can run inside the devcontainer
# Use the Go toolchain to install the latest htmltest binary reliably
RUN apt-get update && apt-get install -y ca-certificates curl && \
        GOBIN=/usr/local/bin /usr/local/go/bin/go install github.com/wjdp/htmltest@latest && \
        if [ ! -x /usr/local/bin/htmltest ]; then \
            echo "htmltest install failed" >&2; exit 1; \
        fi

# Install mermaid prerequistes
RUN apt-get install -y chromium

# Ensure the directory exists before changing ownership
RUN mkdir -p /home/vscode/.gnupg && \
    chown -R vscode:vscode /home/vscode/.gnupg && \
    chmod 700 /home/vscode/.gnupg
