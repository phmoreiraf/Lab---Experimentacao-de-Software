#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

JAR="ck.jar"
if [ -f "$JAR" ]; then
  echo "[CK] ck.jar já existe."
  exit 0
fi

echo "[CK] Baixando ck.jar (release oficial)..."
curl -L -o ck.jar https://github.com/mauricioaniche/ck/releases/latest/download/ck.jar || {
  echo "Falha ao baixar ck.jar automaticamente. Baixe manualmente e coloque em ck/ck.jar."
  exit 1
}
echo "[CK] Pronto: ck/ck.jar"
