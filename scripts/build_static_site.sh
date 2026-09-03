#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
publish_dir="${project_dir}/dist"
api_base="${LAKSHYA_API_BASE:-}"

if [[ ! "${api_base}" =~ ^https?:// ]]; then
  echo "LAKSHYA_API_BASE must be an absolute http(s) URL" >&2
  exit 1
fi

rm -rf "${publish_dir}"
mkdir -p "${publish_dir}"

root_files=(
  app.js payroll-ui.js apple-touch-icon.png auth-shared.css index.html lakshya-logo-576.png
  lakshya-logo.png manifest.webmanifest portal-shared.css push-client.js
  push-service-worker.js push-shared.css pwa-icon-192.png pwa-icon-512.png
  runtime-config.js share-card.png styles.css sw.js
)

for file in "${root_files[@]}"; do
  cp "${project_dir}/${file}" "${publish_dir}/${file}"
done

for directory in attendance-app faculty-app lakshya-site legal parent-app student-app; do
  cp -R "${project_dir}/${directory}" "${publish_dir}/${directory}"
done

escaped_api_base="${api_base//\//\\/}"
sed -i.bak "s/__LAKSHYA_API_BASE__/${escaped_api_base}/g" "${publish_dir}/runtime-config.js"
rm "${publish_dir}/runtime-config.js.bak"

echo "Static portals built in ${publish_dir} using ${api_base}"
