#!/usr/bin/env bash
# Install gitleaks from scripts/tools.lock for linux x64 (GitHub Actions). No third-party actions.
set -euo pipefail

ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
LOCK="${ROOT}/scripts/tools.lock"
SHAFILE="${ROOT}/scripts/ci/tools.sha256"

if [[ ! -f "$LOCK" ]]; then
  echo "install_gitleaks: missing $LOCK" >&2
  exit 1
fi
if [[ ! -f "$SHAFILE" ]]; then
  echo "install_gitleaks: missing $SHAFILE" >&2
  exit 1
fi

VERSION=""
while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%%#*}"
  line="$(echo "$line" | tr -d '[:space:]')"
  [[ -z "$line" ]] && continue
  if [[ "$line" == gitleaks=* ]]; then
    VERSION="${line#gitleaks=}"
    break
  fi
done < "$LOCK"

if [[ -z "$VERSION" ]]; then
  echo "install_gitleaks: gitleaks version not found in tools.lock" >&2
  exit 1
fi

EXPECTED=""
while read -r name ver sum _rest; do
  [[ "$name" == \#* ]] && continue
  [[ -z "$name" ]] && continue
  if [[ "$name" == gitleaks && "$ver" == "$VERSION" ]]; then
    EXPECTED="$sum"
    break
  fi
done < "$SHAFILE"

if [[ -z "$EXPECTED" ]]; then
  echo "install_gitleaks: no checksum recorded for gitleaks ${VERSION} in tools.sha256" >&2
  exit 1
fi

TARBALL="gitleaks_${VERSION}_linux_x64.tar.gz"
URL="https://github.com/gitleaks/gitleaks/releases/download/v${VERSION}/${TARBALL}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl -fsSL -o "${TMP}/${TARBALL}" "$URL"
echo "${EXPECTED}  ${TARBALL}" | (cd "$TMP" && sha256sum -c)
tar -xzf "${TMP}/${TARBALL}" -C "$TMP" gitleaks
chmod +x "${TMP}/gitleaks"

BIN_DIR="${RUNNER_TEMP:-/tmp}/gitleaks-bin"
mkdir -p "$BIN_DIR"
mv "${TMP}/gitleaks" "${BIN_DIR}/gitleaks"
echo "$BIN_DIR" >> "${GITHUB_PATH:?GITHUB_PATH must be set in CI}"
"${BIN_DIR}/gitleaks" version
