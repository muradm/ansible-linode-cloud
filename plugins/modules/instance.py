# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
action: instance
short_description: Create/update/remove a linode instance
description:
    - Using I(label) as identifier creates a linode instance if it does not exist if I(state) is C(present)
      or removes instance if I(state) is C(absent). Currently can update only I(tags) and I(group) fields of
      linode instance. Plugin uses M(linode_api4) python module provided by Linode. Plugin supports
      check mode in the way that; existing linode instances will not be updated/deleted, only B(changed)
      reported as C(true) and returning data reflecting the changes, but instance in the cloud is not affected;
      new linode instances will simulate fake creation with inadequate output. Since this is action only
      plugin one could delegate it B(localhost) or event use it with B(gather_facts) turned off.
options:
  state:
    description:
      - C(present) to create new or manage existing linode instance
      - C(absent) to remote existing linode instance
    choices: [ "present", "absent" ]
    default: "present"
    type: str
  label:
    description: Linode instance label to create/update/remove.
    type: str
    required: true
  region:
    description: Linode region to create instance at.
    type: str
    required: true
  type:
    description: Type of linode instance to create.
    type: str
    required: true
  image:
    description: Image to use for new linode instance.
    type: str
    required: true
  group:
    description: Group field value this linode instance should have.
    type: str
    default: None
    required: false
  tags:
    description: List of tags this linode instance should have.
    type: list
    elements: str
    default: []
    reqired: false
  authorized_keys:
    description: List of ssh keys to add to root user at instance creation time.
    type: list
    elements: str
    default: []
    required: false
  ipv4_public_rdns:
    description: Reverse DNS address for public IPv4 address.
    type: str
    default: None
    required: false
  ipv4_private_ip:
    description: Allocate private IPv4 address.
    type: bool
    default: false
    required: false
  root_pass:
    description: Root password to set at instance creation time.
    type: str
    default: None
    required: false
requirements: [ "linode_api4" ]
notes:
  - I(group) option is being deprecated by Linode.
  - Options marked as required, are required at instance creation time.
  - For update and remove only I(label) is required.
  - I(root_pass) should not be used normally.
  - Region migration is not supported at the moment.
  - Instance resizing is not supported at the moment.
  - Instance rebuilding is not supported at the moment.
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

- name: update my linode tags
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
      - 'monitoring'

- name: remove my linode
  hosts: localhost
  tasks:
  - linode.cloud.instance:
      label: 'my-linode-1'
      state: 'absent'
'''

RETURN = r'''
instance:
  description: The instance description in JSON serialized form.
  returned: Always. When instance deleted contains single field status with value deleted.
  type: dict
  sample: {
      "alerts": {
          "cpu": 360,
          "io": 10000,
          "network_in": 10,
          "network_out": 10,
          "transfer_quota": 80
      },
      "backups": {
          "enabled": false,
          "last_successful": null,
          "schedule": {
              "day": null,
              "window": null
          }
      },
      "created": "2020-12-21T18:54:21",
      "group": "",
      "hypervisor": "kvm",
      "id": 23557736,
      "image": "linode/debian10",
      "ipv4": [
          "w.x.y.z"
      ],
      "ipv6": "aaaa:bbbb::cccc:dddd:eeee:ffff/64",
      "label": "my-linode-1",
      "region": "eu-central",
      "specs": {
          "disk": 163840,
          "gpus": 0,
          "memory": 8192,
          "transfer": 5000,
          "vcpus": 4
      },
      "status": "running",
      "tags": [
          "linodes",
          "db-servers"
      ],
      "type": "g6-standard-4",
      "updated": "2020-12-21T18:54:21",
      "watchdog_enabled": true 
  }
root_pass:
  description: The root password to linode instance.
  returned: Only `root_pass` option was not provided, so that it is generated.
  type: str
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    AnsibleModule(dict()).fail_json('instance is action')


if __name__ == '__main__':
    main()
