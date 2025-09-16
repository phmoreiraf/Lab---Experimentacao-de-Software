#!/usr/bin/env bash
set -euo pipefail

# Caminho deste script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

JAR="$SCRIPT_DIR/ck.jar"
TMP_DIR="$ROOT_DIR/.tmp_ck_ref"

if [ -f "$JAR" ]; then
  echo "[CK-REF] ck.jar já existe em ck/ck.jar."
  exit 0
fi

echo "[CK-REF] Tentando obter ck.jar a partir de um repositório de referência..."
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

# OBS: Ajuste aqui se você quiser clonar um fork específico de extractor CK
#      (o script mantém genérico para não quebrar caso a estrutura mude).
REF_REPO_URL="https://github.com/mauricioaniche/ck.git"

(
  cd "$TMP_DIR"
  # Primeira tentativa: clonar o repositório upstream do CK e construir localmente
  echo "[CK-REF] Clonando upstream CK (build local) ..."
  git clone --depth 1 "$REF_REPO_URL" ck_upstream || true
  if [ -d ck_upstream ]; then
    cd ck_upstream
    # Tenta compilar com Maven/Gradle, se o projeto fornecer
    if [ -f "pom.xml" ]; then
      echo "[CK-REF] Detectado Maven. Tentando mvn -DskipTests package ..."
      mvn -q -DskipTests package || true
      CANDIDATE_JAR="$(find target -maxdepth 1 -name '*.jar' -type f | head -n1 || true)"
      if [ -n "${CANDIDATE_JAR:-}" ] && [ -f "$CANDIDATE_JAR" ]; then
        cp "$CANDIDATE_JAR" "$JAR"
      fi
    elif [ -f "build.gradle" ] || [ -f "gradlew" ]; then
      echo "[CK-REF] Detectado Gradle. Tentando ./gradlew jar ..."
      chmod +x gradlew 2>/dev/null || true
      ./gradlew -q jar || true
      CANDIDATE_JAR="$(find build/libs -maxdepth 1 -name '*.jar' -type f | head -n1 || true)"
      if [ -n "${CANDIDATE_JAR:-}" ] && [ -f "$CANDIDATE_JAR" ]; then
        cp "$CANDIDATE_JAR" "$JAR"
      fi
    fi
  fi
)

if [ -f "$JAR" ]; then
  echo "[CK-REF] ck.jar obtido via build local do upstream."
  rm -rf "$TMP_DIR"
  exit 0
fi

echo "[CK-REF] Não foi possível obter via referência. Fazendo fallback para a release oficial..."
bash "$SCRIPT_DIR/get_ck.sh"
rm -rf "$TMP_DIR"
