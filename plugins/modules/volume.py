# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
action: volume
short_description: Create/update/remove a linode volume
description:
    - Using I(label) as identifier creates a linode volume if it does not exist if I(state) is C(present)
      or removes instance if I(state) is C(absent). Can update I(tags) and I(size) fields of linode
      volume. Plugin uses M(linode_api4) python module provided by Linode. Plugin supports
      check mode in the way that; existing linode volumes will not be updated/deleted, only B(changed)
      reported as B(true) and returning data reflecting the changes, but volume in the cloud is not
      affected; new linode volumes will simulate fake creation with inadequate output. Since this is
      action only plugin one could delegate it B(localhost) or event use it with B(gather_facts) turned off.
options:
  state:
    description:
      - C(present) to create new or manage existing linode volume
      - C(absent) to remote existing linode volume
    choices: [ "present", "absent" ]
    default: "present"
    type: str
  label:
    description: Linode volume label to create/update/remove.
    type: str
    required: true
  region:
    description: Linode region to create volume at.
    type: str
    required: true
  size:
    description: Size of linode volume to create.
    type: int
    required: true
  tags:
    description: List of tags this linode instance should have.
    type: list
    default: []
    elements: str
    reqired: false
requirements: [ "linode_api4" ]
notes:
  - Options marked as required, are required at volume creation time.
  - For update and remove only I(label) is required.
  - Region migration is not supported at the moment.
  - Volume resizing is supported upwards.
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
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

- name: resize my volume and update tags
  hosts: localhost
  tasks:
  - linode.cloud.volume:
      label: 'my-volume-1'
      region: 'eu-central'
      size: 20
      tags:
      - 'linodes'
      - 'db-servers'
      - 'monitoring'

- name: remove my volume
  hosts: localhost
  tasks:
  - linode.cloud.volume:
      label: 'my-volume-1'
      state: 'absent'
'''

RETURN = r'''
volume:
  description: The volume description in JSON serialized form.
  returned: Always. When volume deleted contains single field status with value deleted.
  type: dict
  sample: {
      "created": "2020-12-21T18:54:21",
      "filesystem_path": "/dev/disk/by-id/scsi-0Linode_Volume_my-volume-1",
      "id": 108382,
      "linode_id": null,
      "linode_label": null,
      "label": "my-volume-1",
      "size": 20,
      "region": "eu-central",
      "status": "creating",
      "tags": [
          "linodes",
          "db-servers"
      ],
      "updated": "2020-12-21T18:54:21",
  }
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    AnsibleModule(dict()).fail_json('volume is action')


if __name__ == '__main__':
    main()
