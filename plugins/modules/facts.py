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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: facts
short_description: Gather facts from the local Ansible controller
version_added: '1.0.0'
description:
  - Collects facts from the controller host that is running Ansible.
  - Includes current user information, Python interpreter and pip version,
    and the currently loaded Ansible configuration file.
  - This module runs only on the controller and does not connect to any
    managed node.
options:
  gather_subset:
    description:
      - List of fact subsets to gather.
      - Use C(all) to gather all available facts.
      - Use C(!subset) to exclude specific subsets.
    type: list
    elements: str
    default: [all]
    choices: [all, user, config, python, '!all', '!user', '!config', '!python']
author:
  - oØ.o (@o0-o)
seealso:
  - module: ansible.builtin.setup
notes:
  - This module must be run via its action plugin.
  - Only supported on POSIX-style controller systems.
  - Will raise an error if run from Windows.
attributes:
  check_mode:
    description: This module supports check mode.
    support: full
  async:
    description: This module does not support async operation.
    support: none
  platform:
    description: Only POSIX platforms are supported.
    support: full
    platforms: posix
'''

EXAMPLES = r'''
- name: Gather all controller facts
  o0_o.controller.facts:

- name: Gather only Python information
  o0_o.controller.facts:
    gather_subset:
      - python

- name: Gather user and config info, exclude Python
  o0_o.controller.facts:
    gather_subset:
      - user
      - config
      - '!python'
'''

RETURN = r'''
ansible_facts:
  description: Dictionary of gathered controller facts.
  returned: always
  type: dict
  contains:
    o0_controller:
      description: Nested facts gathered from the controller.
      type: dict
      contains:
        user:
          description: Current controller user info.
          type: dict
          returned: when subset includes 'user'
          contains:
            id:
              type: int
              description: User ID.
            name:
              type: str
              description: Username.
            group:
              type: dict
              description: Primary group info.
              contains:
                id:
                  type: str
                  description: Group ID.
                name:
                  type: str
                  description: Group name.
        config:
          description: Parsed Ansible config file and values.
          type: dict
          returned: when subset includes 'config'
          contains:
            path:
              type: str
              description: Path to the loaded config file.
            settings:
              type: dict
              description: Sectioned config key/values.
        python:
          description: Python and pip information.
          type: dict
          returned: when subset includes 'python'
          contains:
            interpreter:
              type: dict
              description: Python interpreter details.
              contains:
                path:
                  type: str
                  description: Path to the Python interpreter.
                version:
                  type: dict
                  description: Version metadata.
                  contains:
                    id:
                      type: str
                      description: Python version string.
            pip:
              type: dict
              description: pip installation metadata.
              returned: when pip is installed
              contains:
                version:
                  type: dict
                  description: pip version metadata.
                  contains:
                    id:
                      type: str
                      description: pip version string.
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    """Fail if this module is run directly without the action plugin."""
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    module.fail_json(msg='This module must be run via its action plugin.')


if __name__ == '__main__':
    main()
