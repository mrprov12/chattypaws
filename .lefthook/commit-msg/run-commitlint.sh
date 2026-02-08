#!/usr/bin/env bash
set -e
# Source rc so nvm/fnm/node are on PATH when Cursor (or other GUI) runs the hook
if [ -f ./lefthook.rc ]; then
  . ./lefthook.rc
fi
exec ./node_modules/.bin/commitlint --edit "$1"
