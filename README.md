# o0_o.controller

[![Ansible Galaxy](https://img.shields.io/ansible/collection/v/o0_o/controller.svg?color=brightgreen&label=ansible%20galaxy)](https://galaxy.ansible.com/o0_o/controller)

Ansible Collection for gathering facts from the Ansible controller host.

## Overview

The `o0_o.controller` collection provides a controller-side `facts` plugin that collects local environment details from the system executing Ansible — not the remote managed nodes. This is useful for audit logging, playbook diagnostics, and context-aware automation logic that depends on the state of the controller.

### Key Features

- Runs entirely on the controller — no managed node connection required.
- Supports subset filtering for fact collection (`user`, `config`, `python`).
- Safe fallback behavior when `pip` is not available.
- Full `run_once`-safe design, with warning if misused.
- Compatible with check mode.
- Fully covered by unit and integration tests.

## Included Plugins

| Type          | Name      | Description                             |
|---------------|-----------|-----------------------------------------|
| Module        | `facts`   | Controller-only fact collector stub     |
| Action Plugin | `facts`   | Implementation logic for fact gathering |

## Usage

```yaml
- name: Gather all controller facts
  o0_o.controller.facts:

- name: Gather only Python-related facts
  o0_o.controller.facts:
    gather_subset:
      - python

- name: Gather user and config, but skip python
  o0_o.controller.facts:
    gather_subset:
      - user
      - config
      - '!python'
```

## Subsets

You can select specific subsets of facts using the `gather_subset` option.

Available subsets:

- `user`: current UID, username, and group
- `config`: loaded Ansible configuration file and values
- `python`: interpreter path, version, and `pip` version (if present)

You can exclude subsets with a `!` prefix.

## Requirements

- Ansible `2.15+`
- POSIX-compatible controller (not supported on Windows)
- This plugin should be run with `run_once: true`

## Development

This collection follows the same structure and contribution guidelines as [`o0_o.posix`](https://galaxy.ansible.com/o0_o/posix). All source code is hosted at:

**GitHub**: [https://github.com/o0-o/ansible-collection-controller](https://github.com/o0-o/ansible-collection-controller)

Pull requests and issues welcome.

## License

[GPLv3 or later](https://www.gnu.org/licenses/gpl-3.0.txt)

---

© 2025 oØ.o (@o0-o)
