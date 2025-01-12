#!/bin/bash

# Path to the hooks folder in the repository
REPO_HOOKS_DIR="./hooks"

# Path to the .git/hooks directory
GIT_HOOKS_DIR=".git/hooks"

# Ensure the .git/hooks directory exists
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "Error: This script must be run from the root of a Git repository."
    exit 1
fi

# Copy all hooks from the repo hooks folder to the .git/hooks directory
cp -v "$REPO_HOOKS_DIR/"* "$GIT_HOOKS_DIR"

# Make sure the hooks are executable
chmod +x "$GIT_HOOKS_DIR/"*

echo "Hooks installed successfully."

