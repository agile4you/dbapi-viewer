#!/bin/bash
set -e
exec python deploy.py --postgres $CONNSTRING -h 0.0.0.0
