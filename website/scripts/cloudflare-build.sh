#!/usr/bin/env bash

set -euo pipefail

QUARTO_VERSION="${QUARTO_VERSION:-1.9.38}"
INSTALL_DIR=".cf-quarto/${QUARTO_VERSION}"

case "$(uname -m)" in
  x86_64)
    QUARTO_ARCH="amd64"
    ;;
  aarch64|arm64)
    QUARTO_ARCH="arm64"
    ;;
  *)
    echo "Unsupported build architecture: $(uname -m)" >&2
    exit 1
    ;;
esac

if [[ ! -x "${INSTALL_DIR}/bin/quarto" ]]; then
  ARCHIVE="quarto-${QUARTO_VERSION}-linux-${QUARTO_ARCH}.tar.gz"
  DOWNLOAD_URL="https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/${ARCHIVE}"

  mkdir -p "${INSTALL_DIR}"
  curl --fail --location --retry 3 "${DOWNLOAD_URL}" --output "/tmp/${ARCHIVE}"
  tar -xzf "/tmp/${ARCHIVE}" -C "${INSTALL_DIR}" --strip-components=1
fi

python3 -m venv "${INSTALL_DIR}/python"
"${INSTALL_DIR}/python/bin/python3" -m pip install -r requirements.txt
export PATH="${PWD}/${INSTALL_DIR}/python/bin:${PATH}"
"${INSTALL_DIR}/bin/quarto" render
