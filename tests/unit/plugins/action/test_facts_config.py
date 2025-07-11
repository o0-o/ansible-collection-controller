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

import tempfile
import pytest

from ansible.errors import AnsibleActionFail


def test_config_reads_ini(action_base):
    """
    Ensure that the config() collector parses a real INI file correctly,
    extracting the config path and nested settings.
    """
    ini = '[defaults]\ninventory = ./hosts\n'

    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write(ini)
        path = f.name

    task_vars = {'ansible_config_file': path}

    result = action_base.config(task_vars=task_vars)

    assert result['path'] == path
    assert result['settings']['defaults']['inventory'] == './hosts'


def test_config_raises_without_var(action_base):
    """
    Ensure that config() raises AnsibleActionFail when ansible_config_file
    is missing from task_vars.
    """
    with pytest.raises(AnsibleActionFail) as excinfo:
        action_base.config(task_vars={})

    assert 'ansible_config_file' in str(excinfo.value)
