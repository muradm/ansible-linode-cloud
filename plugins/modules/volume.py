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
      - C(detached) to create new or manage existing linode volume in detached state
      - C(attached) to create new or manage existing linode volume in attached state
      - C(absent) to remote existing linode volume
    choices: [ "detached", "attached", "absent" ]
    default: "detached"
    type: str
  label:
    description:
        A 1..32 characters Volume’s label, which is also used in the I(filesystem_path) of the resulting volume.
    type: str
    required: true
  region:
    description:
        The Region to deploy this Volume in. This is only required if a I(instance) is not given and ignored
        in this case.
    type: str
    required: false
  size:
    description:
        The initial size of this volume, in GB. Be aware that volumes may only be resized up after creation.
    type: int
    required: false
    default: 20
  tags:
    description: List of tags this linode instance should have.
    type: list
    default: []
    elements: str
    reqired: false
  instance:
    description:
        Label of instance to attach this volume to. Otherwise volume will be unattached, and can be
        attached to instance later on. Mandatory if I(state) is set to C(attached) otherwise ignored.
    type: str
    required: false
  force:
    description:
        When state is C(absent) and volume attached, volume cannot be remove. If I(force) is C(True)
        will automatically detach and then remove volume.
    type: bool
    required: false
    default: false
requirements: [ "linode_api4", "cerberus" ]
notes:
  - Options marked as required, are required at volume creation time.
  - For update and remove only I(label) is required.
  - Region migration is not supported at the moment.
  - Volume resizing is supported upwards.
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.volume:
        label: my-unattached-volume-1
        region: 'eu-central'
        tags:
        - 'linodes'
        - 'db-servers'
        size: 10


- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.instance:
        label: 'my-linode-1'
        type: 'g6-standard-1'
        image: 'linode/debian10'
        region: 'eu-central'
        tags:
        - 'linodes'
        - 'db-servers'

    - muradm.linode.volume:
        label: 'my-volume-1'
        instance: 'my-linode-1'
        state: 'attached'
        size: 10


- name: resize my volume and update tags
  hosts: localhost
  tasks:
  - muradm.linode.volume:
      label: 'my-volume-1'
      region: 'eu-central'
      size: 20
      tags:
      - 'linodes'
      - 'db-servers'
      - 'monitoring'


# attach existing volume to existing instance
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.volume:
        label: my-unattached-volume-1
        instance: 'my-linode-1'
        state: 'attached'


# detach arbitrary existing volume
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.volume:
        label: my-volume-1
        state: detached


# remove arbitrary volume
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.volume:
        label: my-volume-1
        state: absent
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
