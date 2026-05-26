#!/bin/sh
# Build localhost/boundary:latest from local vse-sync-test + vse-sync-collection-tools.
#
# Usage:
#   ./vse-sync-test/cmd/build-image.sh
#   ./vse-sync-test/cmd/build-image.sh /path/to/parent-dir
#
# parent-dir must contain:
#   vse-sync-test/
#   vse-sync-collection-tools/

set -e

ROOT="${1:-.}"
ROOT=$(cd "$ROOT" && pwd)

for repo in vse-sync-collection-tools vse-sync-test; do
	if [ ! -d "${ROOT}/${repo}" ]; then
		echo "error: missing ${ROOT}/${repo}" >&2
		echo "Build context must be the parent of both repos." >&2
		echo "Example layout:" >&2
		echo "  parent/vse-sync-collection-tools/" >&2
		echo "  parent/vse-sync-test/" >&2
		exit 1
	fi
done

echo "Building from ${ROOT} ..."
podman build --no-cache -f "${ROOT}/vse-sync-test/Containerfile" -t localhost/boundary:latest "${ROOT}"

echo "Done: localhost/boundary:latest"
