# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
action: balancer_node
short_description: Create/update/remove a linode balancer node
description:
    - Action will query by I(balancer) and I(port) existing cloud state, then by I(address)
      will manage balancer node only.
    - Fails with AnsibleError if specified I(balancer) or its I(port) configuration does exist
    - Linode internal IDs are not used to perform operations, thus updating I(balancer), I(port)
      and I(address) here impossible. Other fields I(label), I(mode) and I(weight) updatable here.
options:
  state:
    description:
      - C(present) to create new or manage existing linode balancer node
      - C(absent) to remote existing linode balancer node
    choices: [ "present", "absent" ]
    default: "present"
    type: str
  balancer:
    description:
        A 3..32 characters long existing balancer label.
    type: str
    required: true
  port:
    description:
        Port configuration on I(balancer) where to query this node by its I(address).
    type: int
    required: true
  address:
    description:
        The private IP Address and port in the form B(address:port) where this backend can be reached.
        This must be a B(private) IP address.
    type: str
    required: true
  label:
    description:
        A 3..32 characters long label for this node. This is for display purposes only.
    type: str
    required: true
  mode:
    description:
        The mode balancer should use when sending traffic to this backend.
        - C(accept) - backend is accepting traffic
        - C(reject) - backend will not receive traffic
        - C(drain) - backend will not receive new traffic, but connections already pinned to it will continue to be routed to it
        - C(backup) - backend will only receive traffic if all accept nodes are down
    choices: [ "accept", "reject", "drain", "backup" ]
    type: str
    required: false
    default: "accept"
  weight:
    description:
        Weight of this node in the range 1..255. Used when picking a backend to serve a request and is not
        pinned to a single backend yet. Nodes with a higher weight will receive more traffic.
    type: int
    required: false
    default: 1
requirements: [ "linode_api4", "cerberus" ]
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
# control single balanced node configuration
# test-lb-1 balancer and its 80 port configuration should be performed elsewhere
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer_node:
        balancer: test-lb-1
        port: 80
        address: 192.168.166.192:8080
        label: 'test-node-1'
        mode: 'accept'
        weight: 3
        state: present

# remove this specific node configuration from balancer
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer_node:
        balancer: test-lb-1
        port: 80
        address: 192.168.166.192:8080
        state: absent
'''

RETURN = r'''
balancer_node:
  description: The volume description in JSON serialized form.
  returned: Always. When volume deleted contains single field status with value deleted.
  type: dict
  sample: {
    "address": "192.168.166.192:8080",
    "config_id": 135043,
    "id": 13637491,
    "label": "test-node-1",
    "mode": "accept",
    "nodebalancer_id": 110572,
    "status": "UP",
    "weight": 1
  }
'''


def main():
    AnsibleModule(dict()).fail_json('balancer_node is action')


if __name__ == '__main__':
    main()
