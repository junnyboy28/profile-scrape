#!/bin/bash
set -e

# Install Playwright browsers if not already installed
playwright install chromium
playwright install-deps

cd /app