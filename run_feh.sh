#!/usr/bin/env bash
ARCHILLECT_DIR=${ARCHILLECT_DIR:-~/.opt/archillect-load/}
python $ARCHILLECT_DIR/archillect.py && feh --bg-max $ARCHILLECT_DIR/archillect.jpg
