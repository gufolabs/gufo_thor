#!/bin/sh
# ---------------------------------------------------------------------
# Gufo Thor Init Script
# This is a little script which can be downloaded from internet
# to install Gufo Thor and initialize NOC.
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

set -e

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
    if test "$major_version" -ge 3 && test "$minor_version" -ge 8; then
        echo "Python $python_version is installed."
    else
        echo "Python 3.8 or later is required. Exiting."
        exit 1
    fi
else
    echo "Python is not installed. Exiting."
    exit 1
fi

# Install Gufo Thor
pip3 install --upgrade gufo-thor

# Run
gufo-thor up