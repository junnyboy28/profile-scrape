#!/bin/bash
set -e


playwright install chromium
playwright install-deps

cd /app