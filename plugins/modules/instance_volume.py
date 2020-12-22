# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
action: instance_volume
short_description: Attach/Detach a linode volume to linode instance
description:
    - Based on I(state) either attaches or detaches volume to/from instance. Supports check mode.
options:
  state:
    description:
      - C(present) attach volume to instance if not attached
      - C(absent) detach volume from instance if attached
    choices: [ "present", "absent" ]
    default: "present"
    type: str
  instance:
    description: Linode instance label to attach/detach I(volume) to/from.
    type: str
    required: true
  volume:
    description: Linode volume label to atttach/detach I(instance) to/from.
    type: str
    required: true
requirements: [ "linode_api4" ]
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
- name: create my linode instance
  hosts: localhost
  tasks:
  - linode.cloud.instance:
      label: 'my-linode-1'
      type: 'g6-standard-1'
      image: 'linode/debian10'
      region: 'eu-central'
      tags:
      - 'linodes'
      - 'db-servers'

- name: create my linode volume
  hosts: localhost
  tasks:
  - linode.cloud.volume:
      label: 'my-volume-1'
      region: 'eu-central'
      size: 10
      tags:
      - 'linodes'
      - 'db-servers'

- name: attach volume to instance
  hosts: localhost
  tasks:
  - linode.cloud.instance_volume:
      instance: 'my-linode-1'
      volume: 'my-volume-1'

- name: detach volume from instance
  hosts: localhost
  tasks:
  - linode.cloud.instance_volume:
      instance: 'my-linode-1'
      volume: 'my-volume-1'
      state: 'absent'
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    AnsibleModule(dict()).fail_json('instance_volume is action')


if __name__ == '__main__':
    main()
