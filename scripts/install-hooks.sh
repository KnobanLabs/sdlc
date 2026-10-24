#!/usr/bin/env bash
# Copyright 2026 Knoban LLC
# SPDX-License-Identifier: MIT
# (https://github.com/KnobanLabs/sdlc)

# Turns on the hooks in .githooks/ for this clone (CONTRIBUTING.md, Secret scan
# before each commit), by pointing core.hooksPath at them. Run it again after
# a fresh clone; `git config --unset core.hooksPath` turns them off.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
chmod +x .githooks/*
git config core.hooksPath .githooks
echo "Hooks on: core.hooksPath is .githooks. The secret scan needs Docker running."
