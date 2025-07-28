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

import pytest

from ansible.errors import AnsibleActionFail


def test_run_blocks_on_windows(monkeypatch, action_base) -> None:
    """Test run method blocks on Windows systems."""
    monkeypatch.setattr(os, "name", "nt")

    with pytest.raises(AnsibleActionFail) as excinfo:
        action_base.run(task_vars={})

    assert "does not support Windows" in str(excinfo.value)
