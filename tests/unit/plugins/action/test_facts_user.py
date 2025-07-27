# vim: ts=4:sw=4:sts=4:et:ft=python
# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; -*-
#
# GNU General Public License v3.0+
# SPDX-License-Identifier: GPL-3.0-or-later
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Copyright (c) 2025 oØ.o (@o0-o)
#
# This file is part of the o0_o.controller Ansible Collection.

from __future__ import annotations

import os
import subprocess


def test_user(monkeypatch, action_base) -> None:
    """Test user collector gathers controller user information."""
    monkeypatch.setattr(os, 'geteuid', lambda: 1000)

    def mock_run(args, capture_output, encoding, check):
        if '-un' in args:
            return type('Result', (), {'stdout': 'testuser\n'})()
        if '-g' in args:
            return type('Result', (), {'stdout': '1000\n'})()
        if '-gn' in args:
            return type('Result', (), {'stdout': 'testgroup\n'})()
        raise ValueError(f"Unexpected args: {args}")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = action_base.user()

    assert result['id'] == 1000
    assert result['name'] == 'testuser'
    assert result['group']['id'] == '1000'
    assert result['group']['name'] == 'testgroup'
