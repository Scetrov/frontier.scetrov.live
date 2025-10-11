FROM mcr.microsoft.com/devcontainers/javascript-node:20

# Build arguments: choose non-root username/uid/gid. Default to 'node' to match
# the base devcontainer image's default non-root user. Override in build args if needed.
ARG USERNAME=node
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

ENV DEBIAN_FRONTEND=noninteractive

USER root

# Install required tooling in a rootless-friendly way.
# We avoid apt (which fails under some rootless userns mappings) and instead
# download a Hugo binary directly and install optional tools with npm/pip if
# the runtimes are present in the base image.
RUN set -eux; \
  # Install Hugo (extended) from GitHub releases into /usr/local/bin if possible
  HUGO_URL="https://github.com/gohugoio/hugo/releases/latest/download/hugo_extended_Linux-64bit.tar.gz"; \
  (curl -fsSL "$HUGO_URL" -o /tmp/hugo.tar.gz || wget -qO /tmp/hugo.tar.gz "$HUGO_URL") && \
  tar -xzf /tmp/hugo.tar.gz -C /tmp || true; \
  if [ -f /tmp/hugo ]; then mv /tmp/hugo /usr/local/bin/hugo && chmod 0755 /usr/local/bin/hugo; else echo "hugo binary not found after download, skipping"; fi; \
  rm -f /tmp/hugo.tar.gz; rm -rf /tmp/hugo*; \
  # Try to install markdownlint-cli globally if npm is available
  if command -v npm >/dev/null 2>&1; then npm install --global markdownlint-cli || echo "npm markdownlint install failed"; else echo "npm not found, skipping markdownlint"; fi; \
  # If python3 is present, try to upgrade pip and install pre-commit
  if command -v python3 >/dev/null 2>&1; then \
  python3 -m pip install --upgrade pip pre-commit || echo "pip install failed or pip missing"; \
  else \
  echo "python3 not found, skipping pip/pre-commit install"; \
  fi; \
  # Informational: git/make/curl/wget/ca-certificates/gnupg may not be present in
  # the base image under rootless environments; prefer images that include them
  command -v git >/dev/null 2>&1 || echo "git not found in base image"; \
  command -v make >/dev/null 2>&1 || echo "make not found in base image";

# Create a non-root user if it doesn't exist. Use the provided UID/GID.
RUN if id -u ${USERNAME} >/dev/null 2>&1; then echo "user exists"; else \
  # Create group only if the requested GID is not already in use
  if ! getent group ${USER_GID} >/dev/null 2>&1; then \
  groupadd --gid ${USER_GID} ${USERNAME} || true; \
  else \
  echo "GID ${USER_GID} already exists on system, skipping groupadd"; \
  fi; \
  # Create user only if UID not already present
  if ! getent passwd ${USER_UID} >/dev/null 2>&1; then \
  useradd -s /bin/bash --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} || true; \
  else \
  echo "UID ${USER_UID} already exists on system, skipping useradd"; \
  fi; \
  fi

# Prepare GNUPGHOME in the user's home and set correct ownership so gpg can create
# temporary files/locks there, while the host agent socket will be mounted into it.
RUN set -eux; \
  # Prefer placing GNUPG in the user's home, but some base images/FS layouts
  # may not allow creating /home/${USERNAME} during build. Be tolerant and
  # fall back to a tmp location if necessary.
  if mkdir -p /home/${USERNAME}/.gnupg 2>/dev/null; then \
  chmod 700 /home/${USERNAME}/.gnupg || true; \
  chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.gnupg || true; \
  else \
  echo "Could not create /home/${USERNAME}/.gnupg, creating fallback /tmp/${USERNAME}_gnupg"; \
  mkdir -p /tmp/${USERNAME}_gnupg; chmod 700 /tmp/${USERNAME}_gnupg || true; \
  fi

WORKDIR /workspace

# NOTE: we intentionally do not switch to the non-root user at build time because
# some rootless container runtimes will attempt to chown the WORKDIR to the
# user and fail (invalid argument). The devcontainer / runtime can still run
# as a non-root user when launching the container if desired.

CMD ["sleep", "infinity"]
