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

import subprocess
import sys

import pytest

from ansible.errors import AnsibleActionFail


def test_python_info(monkeypatch, action_base) -> None:
    """Test python collector returns interpreter and pip information."""
    monkeypatch.setattr(sys, "version", "3.12.1 (main, Jan 1 2025) ...")

    def mock_run(args, capture_output, encoding, check):
        return type("Result", (), {"stdout": "pip 24.0 from ..."})()

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = action_base.python(
        task_vars={"ansible_playbook_python": "/usr/bin/python3"}
    )

    assert result["interpreter"]["path"] == "/usr/bin/python3"
    assert result["interpreter"]["version"]["id"] == "3.12.1"
    assert result["pip"]["version"]["id"] == "24.0"


def test_python_raises_without_interpreter(action_base) -> None:
    """Test python raises error when ansible_playbook_python missing."""
    with pytest.raises(AnsibleActionFail) as excinfo:
        action_base.python(task_vars={})

    assert "ansible_playbook_python" in str(excinfo.value)
