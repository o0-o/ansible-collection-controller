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

import pytest

from ansible.errors import AnsibleActionFail


def test_collector_all(monkeypatch, action_base):
    """
    Verify that collector() gathers all available subsets when 'all' is passed.
    """
    monkeypatch.setattr(action_base, 'user', lambda **_: {'u': 1})
    monkeypatch.setattr(action_base, 'config', lambda **_: {'c': 2})
    monkeypatch.setattr(action_base, 'python', lambda **_: {'p': 3})

    result = action_base.collector(gather_subset=['all'])

    assert result['o0_controller']['user'] == {'u': 1}
    assert result['o0_controller']['config'] == {'c': 2}
    assert result['o0_controller']['python'] == {'p': 3}


def test_collector_exclude(monkeypatch, action_base):
    """
    Verify that specific subsets can be excluded using '!subset' syntax.
    """
    monkeypatch.setattr(action_base, 'user', lambda **_: {'u': 1})
    monkeypatch.setattr(action_base, 'config', lambda **_: {'c': 2})
    monkeypatch.setattr(action_base, 'python', lambda **_: {'p': 3})

    result = action_base.collector(gather_subset=['all', '!config'])

    assert 'config' not in result['o0_controller']
    assert 'user' in result['o0_controller']
    assert 'python' in result['o0_controller']


def test_collector_invalid_subset(action_base):
    """
    Verify that collector() raises AnsibleActionFail for invalid subset names.
    """
    with pytest.raises(AnsibleActionFail) as excinfo:
        action_base.collector(gather_subset=['bogus'])

    assert 'Invalid gather_subset' in str(excinfo.value)
