#!/bin/sh
# ---------------------------------------------------------------------
# Gufo Thor Init Script
# This is a little script which can be downloaded from internet
# to install Gufo Thor and initialize NOC.
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Check for docker
if docker version &> /dev/null; then
    echo "docker is installed"
else
    echo "docker is not installed. Exiting"
    exit 1
fi

# Check for docker compose
if docker compose version &> /dev/null; then
    echo "docker compose is installed"
else
    if docker-compose version &> /dev/null; then
        echo "docker-compose is installed"
    else
        echo "docker compose is not installed. Exiting"
        exit 1
    fi
fi

# Check for python
if command -v python3 &> /dev/null; then
    # Get the Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    major_version=$(echo "$python_version" | cut -d'.' -f1)
    minor_version=$(echo "$python_version" | cut -d'.' -f2)
    # Compare the version
    if [[ "$major_version" -ge 3 && "$minor_version" -ge 8 ]]; then
        echo "Python $python_version is installed."
    else
        echo "Python 3.8 or later is required. Exiting."
        exit 1
    fi
else
    echo "Python is not installed. Exiting."
    exit 1
fi

# Parse command-line arguments
mode=""
for arg in "$@"; do
    case "$arg" in
        mode=venv)
            mode="venv"
            ;;
        mode=global)
            mode="global"
            ;;
    esac
done

# Initialize venv, when necessary
if [[ "$mode" -eq "venv" ]]; then
    python -m venv .
    source ./bin/activate
fi

# Install Gufo Thor
pip install --upgrade gufo-thor

# Run
gufo-thor up