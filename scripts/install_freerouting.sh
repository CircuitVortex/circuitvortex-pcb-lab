#!/bin/sh
set -eu
mkdir -p "${1:-/opt/freerouting}"
base="${1:-/opt/freerouting}"
url="https://github.com/freerouting/freerouting/releases/download/v2.2.4/freerouting-2.2.4.jar"
curl -fL "$url" -o "$base/freerouting.jar"
echo "Installed $base/freerouting.jar"
