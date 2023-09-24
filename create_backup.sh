#!/bin/bash
BACKUP_NAME=Slime-bot-for-DC_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=.backup
BACKUP_FILE=${BACKUP_DIR}/${BACKUP_NAME}.tar.bz2
mkdir -p "${BACKUP_DIR}"
find . -type f | grep -Pv '/(.backup|.cache|.git|.upm|__pycache__|log|venv)/' | sed 's|^./||' | LC_COLLATE=C sort | xargs tar -cjvf "${BACKUP_FILE}" &&
  echo "> ${BACKUP_FILE}" ||
  echo "* failed to backup"
