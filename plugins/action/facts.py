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

import configparser
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    """Gather facts relating to the Ansible controller host.

    This action plugin collects information about the Ansible controller
    host including user details, Python interpreter information, and
    Ansible configuration settings. Since it operates on the controller
    host, it does not require a connection to remote hosts.

    The plugin provides modular fact collection through subset filtering
    and supports comprehensive controller environment introspection.

    .. note::
       This plugin operates locally on the controller and does not
       require a connection to remote hosts.
    """

    TRANSFERS_FILES = False
    _requires_connection = False
    _supports_check_mode = True
    _supports_async = False
    _supports_diff = False

    def user(self, task_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return current controller user ID, username, and group info.

        Collects information about the user running the Ansible controller
        process including user ID, username, primary group ID, and group name.

        :param Optional[Dict[str, Any]] task_vars: Task variables dictionary
        :returns Dict[str, Any]: User information dictionary with id, name,
            and group details
        :raises AnsibleActionFail: If any subprocess call fails
        """
        task_vars = task_vars or {}
        self._display.v("Collecting controller user info...")

        user_id = os.geteuid()

        try:
            user_name = subprocess.run(
                ['id', '-un', '--', str(user_id)],
                capture_output=True,
                encoding='utf-8',
                check=True
            ).stdout.rstrip('\r\n')

            group_id = subprocess.run(
                ['id', '-g', '--', str(user_id)],
                capture_output=True,
                encoding='utf-8',
                check=True
            ).stdout.rstrip('\r\n')

            group_name = subprocess.run(
                ['id', '-gn', '--', str(user_id)],
                capture_output=True,
                encoding='utf-8',
                check=True
            ).stdout.rstrip('\r\n')

        except subprocess.CalledProcessError as e:
            raise AnsibleActionFail(f"Failed to get user info: {e}") from e

        return {
            'id': user_id,
            'name': user_name,
            'group': {
                'id': group_id,
                'name': group_name
            }
        }

    def config(self, task_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Read Ansible config file as specified in task_vars.

        Parses the Ansible configuration file and extracts all sections
        and their settings for controller introspection.

        :param Optional[Dict[str, Any]] task_vars: Task variables dictionary
        :returns Dict[str, Any]: Configuration dictionary with path and
            settings information
        :raises AnsibleActionFail: If ansible_config_file is missing from
            task_vars
        """
        task_vars = task_vars or {}
        self._display.v("Collecting controller Ansible config info...")

        path = task_vars.get('ansible_config_file')
        if not path:
            raise AnsibleActionFail(
                "'ansible_config_file' is missing from task_vars"
            )

        config = {'path': path, 'settings': {}}

        cfg = configparser.ConfigParser()
        cfg.read(path)

        for section in cfg.sections():
            config['settings'][section] = dict(cfg.items(section))

        return config

    def python(self, task_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return Python interpreter info and pip version (if available).

        Collects information about the Python interpreter running Ansible
        and attempts to determine the pip version if available.

        :param Optional[Dict[str, Any]] task_vars: Task variables dictionary
        :returns Dict[str, Any]: Python interpreter and pip information
        :raises AnsibleActionFail: If ansible_playbook_python is missing
            from task_vars
        """
        task_vars = task_vars or {}
        self._display.v("Collecting controller Python info...")

        path = task_vars.get('ansible_playbook_python')
        if not path:
            raise AnsibleActionFail(
                "'ansible_playbook_python' is missing from task_vars"
            )

        python = {
            'interpreter': {
                'path': path,
                'version': {
                    'id': sys.version.split()[0]
                }
            }
        }

        try:
            # Try to get pip version from the same interpreter
            pip_argv = [path, '-m', 'pip', '--version']
            pip_output = subprocess.run(
                pip_argv, capture_output=True, encoding='utf-8', check=True
            ).stdout.rstrip('\r\n')
            python['pip'] = {
                'version': {'id': pip_output.split()[1]}
            }
        except Exception:
            self._display.vv("pip not available for this interpreter")
            python['pip'] = None

        return python

    def collector(
        self, gather_subset: Optional[List[str]] = None, task_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run selected collectors and return merged fact data.

        Coordinates the collection of different fact categories based on
        the specified subset filter, supporting modular fact gathering.

        :param Optional[List[str]] gather_subset: Collector subset names
            or ['all']
        :param Optional[Dict[str, Any]] task_vars: Task variables from
            controller
        :returns Dict[str, Any]: Merged fact data under o0_controller
            namespace
        :raises AnsibleActionFail: When invalid gather_subset values are
            provided
        """
        gather_subset = gather_subset or ['all']
        task_vars = task_vars or {}

        all_collectors = ['user', 'config', 'python']
        subsets = set()

        for s in gather_subset:
            if s == 'all':
                subsets = set(all_collectors)
            elif s == '!all':
                subsets = set()
            elif s.startswith('!') and s[1:] in all_collectors:
                subsets.discard(s[1:])
            elif s in all_collectors:
                subsets.add(s)
            else:
                raise AnsibleActionFail(f"Invalid gather_subset: {s}")

        facts = {}
        for s in all_collectors:
            if s in subsets:
                self._display.vv(f"Gathering controller fact subset: {s}")
                facts[s] = getattr(self, s)(task_vars=task_vars)

        return {'o0_controller': facts}

    def run(
        self, tmp: Optional[str] = None, task_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main entry point for the controller facts action plugin.

        Gathers facts about the Ansible controller host based on the
        specified subset filter and returns them under the o0_controller
        fact namespace.

        :param Optional[str] tmp: Temporary directory path (unused)
        :param Optional[Dict[str, Any]] task_vars: Task variables dictionary
        :returns Dict[str, Any]: Standard Ansible result dictionary
        :raises AnsibleActionFail: When running on Windows controllers or
            invalid gather_subset values are provided

        .. note::
           This method operates locally on the controller host and does
           not require a connection to remote hosts. It warns when not
           run with run_once: true.
        """
        task_vars = task_vars or {}
        tmp = None  # tmp is unused in modern Ansible

        if not self._task.run_once:
            self._display.warning(
                "The o0_o.controller.facts module is intended to run on the "
                "controller with `run_once: true`. Running this per-host is "
                "unnecessary."
            )

        # Fail early if run from a Windows controller
        if os.name == 'nt':
            raise AnsibleActionFail(
                "The 'o0_o.controller.facts' plugin does not support Windows "
                "as a controller host. This plugin uses POSIX-only tools."
            )

        argument_spec = {
            'gather_subset': {
                'type': 'list',
                'elements': 'str',
                'default': ['all'],
                'choices': [
                    'all', 'user', 'config', 'python',
                    '!all', '!user', '!config', '!python'
                ]
            }
        }

        validation_result, new_module_args = self.validate_argument_spec(
            argument_spec=argument_spec
        )
        gather_subset = new_module_args['gather_subset']

        result = super(ActionModule, self).run(tmp, task_vars)

        result.update({
            'ansible_facts': self.collector(
                gather_subset=gather_subset,
                task_vars=task_vars
            )
        })

        return result
