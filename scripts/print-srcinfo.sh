#!/usr/bin/env bash
# Run the canonical Arch metadata generator; never hand-maintain .SRCINFO.
set -euo pipefail
cd "$(dirname "$0")/../packaging/aur/jms-bin"
exec makepkg --printsrcinfo
