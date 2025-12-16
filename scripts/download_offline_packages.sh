#!/bin/bash
# Download Python packages for offline/air-gapped installation
#
# Usage:
#   ./scripts/download_offline_packages.sh
#
# This script downloads all required Python packages as wheel files
# to the offline_packages/ directory. Transfer this directory to your
# air-gapped environment for offline installation.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OFFLINE_DIR="$PROJECT_ROOT/offline_packages"

echo "=============================================="
echo "Downloading packages for offline installation"
echo "=============================================="

# Create offline packages directory
mkdir -p "$OFFLINE_DIR"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is required but not found"
    exit 1
fi

# Download packages for multiple platforms
echo ""
echo "Downloading packages..."
echo ""

# Download for current platform
pip3 download \
    -r "$PROJECT_ROOT/requirements.txt" \
    -d "$OFFLINE_DIR" \
    --no-cache-dir

# Also download pip, setuptools, wheel for bootstrapping
pip3 download \
    pip setuptools wheel \
    -d "$OFFLINE_DIR" \
    --no-cache-dir

echo ""
echo "=============================================="
echo "Download complete!"
echo "=============================================="
echo ""
echo "Packages saved to: $OFFLINE_DIR"
echo ""
echo "Contents:"
ls -la "$OFFLINE_DIR"
echo ""
echo "To install in an air-gapped environment:"
echo ""
echo "  1. Copy the 'offline_packages/' directory to the target machine"
echo "  2. Run: pip install --no-index --find-links=offline_packages/ -r requirements.txt"
echo ""
echo "See docs/OFFLINE_INSTALLATION.md for detailed instructions."
