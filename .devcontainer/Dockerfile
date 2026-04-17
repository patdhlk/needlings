FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Install ubc (pinned version; update on release)
# Placeholder URL — replace with the real release asset when it's published.
ARG UBC_VERSION=0.28.1
RUN curl -sSL -o /usr/local/bin/ubc \
      "https://github.com/useblocks/ubcode-pub/releases/download/v${UBC_VERSION}/ubc-linux" \
    && chmod +x /usr/local/bin/ubc \
    || echo "ubc download failed; chapter 6+ will need manual install" >&2
