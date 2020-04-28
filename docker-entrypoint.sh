#!/bin/sh
set -e
if [ "$1" == "run" ]; then
    cd /root/src/antze
    exec /usr/bin/env python3 ao_killboard.py
fi
exec "$@"
