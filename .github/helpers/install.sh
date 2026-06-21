#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK_DIR="${RUNNER_TEMP:-/tmp}/mysite-bench"

python -m pip install --upgrade pip
python -m pip install frappe-bench

rm -rf "${WORK_DIR}"
bench init "${WORK_DIR}" --frappe-branch version-15 --skip-redis-config-generation

cd "${WORK_DIR}"
bench get-app mysite "${ROOT_DIR}"

bench new-site test_site \
  --admin-password admin \
  --mariadb-root-password root \
  --db-host 127.0.0.1 \
  --db-port 3306 \
  --no-mariadb-socket

bench --site test_site install-app mysite

echo "BENCH_DIR=${WORK_DIR}" >> "${GITHUB_ENV}"
