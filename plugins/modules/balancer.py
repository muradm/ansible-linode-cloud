# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
action: balancer
short_description: Create/update/remove a linode balancer
description:
    - Action will query existing balancer by I(label).
    - Linode internal IDs are not used to perform operations, thus updating balancer config
      port here, will effectively drop old port configuration and create new port configuration
      if I(keep_unknown_configs) is set to C(False). If you change I(port) in ansible playbook,
      and I(keep_unknown_configs) is set to C(True) which is default, you effectively will
      create new port configuration.
options:
  state:
    description:
      - C(present) to create new or manage existing linode balancer
      - C(absent) to remote existing linode balancer
    choices: [ "present", "absent" ]
    default: "present"
    type: str
  label:
    description:
        A 3..32 characters long existing balancer label. 
    type: str
    required: true
  region:
    description:
        The ID of the Region to create this NodeBalancer in.
    type: str
    required: true
  client_conn_throttle:
    description:
        Throttle connections per second. Set to 0 zero, which is default, to disable throttling. In the range 0..20.
    type: int
    required: false
  configs:
    description:
        Loadbalancer port configuration that should be defined on this loadbalancer. For the field details,
        refer to B(balancer_config) action. Also
        see related I(keep_unknown_configs) and I(return_unknown_configs).
    type: str
    required: true
  keep_unknown_configs:
    description:
        When managing balancer using this action, if I(configs) field is not configured, but configs actually configured
        from elsewhere, this should remain C(True). When set to C(False), B(balancer) action will consider I(configs)
        an exhaustive list of configs that should be configured under this balancer. Thus, if I(configs) is empty,
        B(balancer) action will also empty the configuration in the cloud.
    type: bool
    required: false
    default: true
  return_unknown_configs:
    description:
        When partially or not managing I(configs) by this action, if this is set to C(True), result will include
        the configs configured from elsewhere, otherwise returns will include only configs listed in I(configs).
    type: bool
    required: false
    default: false
  ipv4_public_rdns:
    description: Reverse DNS address for public IPv4 address.
    type: str
    default: None
    required: false
requirements: [ "linode_api4", "cerberus" ]
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
# completely control balancer in one action
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer:
        label: test-lb-1
        region: 'eu-central'
        keep_unknown_configs: false # will remove configurations added from elsewhere on next run
        configs:
          - {
              port: 80,
              protocol: http,
              algorithm: leastconn,
              stickiness: table,
              nodes: [
                { address: '192.168.153.123:8080', label: 'ds-man-01', mode: 'accept', weight: 1 },
                { address: '192.168.161.168:8080', label: 'ds-man-02', mode: 'accept', weight: 2 },
                { address: '192.168.130.46:8080', label: 'ds-man-03', mode: 'backup', weight: 3 }
              ]
            }
          - {
              port: 443,
              protocol: http,
              algorithm: roundrobin,
              stickiness: table,
              nodes: [
                { address: '192.168.153.123:8443', label: 'ds-man-01', mode: 'accept', weight: 1 },
                { address: '192.168.161.168:8443', label: 'ds-man-02', mode: 'accept', weight: 1 },
                { address: '192.168.130.46:8443', label: 'ds-man-03', mode: 'backup', weight: 1 }
              ]
            }


# just make sure that balancer labeled test-lb-1 exists
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer:
        label: test-lb-1
        region: 'eu-central'


# remove this specific balancer
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer:
        label: test-lb-1
        region: 'eu-central'
        state: absent
'''

RETURN = r'''
balancer:
  description: The balancer description in JSON serialized form.
  returned: Always. When balancer deleted contains single field status with value deleted.
  type: dict
  sample: {
    "client_conn_throttle": 0,
    "configs": [
        {
            "algorithm": "roundrobin",
            "check": "none",
            "check_attempts": 3,
            "check_body": "",
            "check_interval": 0,
            "check_passive": true,
            "check_path": "",
            "check_timeout": 30,
            "cipher_suite": "recommended",
            "id": 135031,
            "nodebalancer_id": 110572,
            "nodes": [
                {
                    "address": "192.168.153.123:8443",
                    "config_id": 135031,
                    "id": 13637219,
                    "label": "ds-man-01",
                    "mode": "accept",
                    "nodebalancer_id": 110572,
                    "status": "UP",
                    "weight": 1
                },
                {
                    "address": "192.168.161.168:8443",
                    "config_id": 135031,
                    "id": 13637220,
                    "label": "ds-man-02",
                    "mode": "accept",
                    "nodebalancer_id": 110572,
                    "status": "UP",
                    "weight": 1
                },
                {
                    "address": "192.168.130.46:8443",
                    "config_id": 135031,
                    "id": 13637221,
                    "label": "ds-man-03",
                    "mode": "backup",
                    "nodebalancer_id": 110572,
                    "status": "UP",
                    "weight": 1
                }
            ],
            "nodes_status": {
                "down": 3,
                "up": 0
            },
            "port": 443,
            "protocol": "http",
            "proxy_protocol": "none",
            "ssl_cert": null,
            "ssl_commonname": "",
            "ssl_fingerprint": "",
            "ssl_key": null,
            "stickiness": "table"
        },
        {
            "algorithm": "leastconn",
            "check": "none",
            "check_attempts": 3,
            "check_body": "",
            "check_interval": 0,
            "check_passive": true,
            "check_path": "",
            "check_timeout": 30,
            "cipher_suite": "recommended",
            "id": 135043,
            "nodebalancer_id": 110572,
            "nodes": [
                {
                    "address": "192.168.153.123:8080",
                    "config_id": 135043,
                    "id": 13637491,
                    "label": "ds-man-01",
                    "mode": "accept",
                    "nodebalancer_id": 110572,
                    "status": "UP",
                    "weight": 1
                },
                {
                    "address": "192.168.161.168:8080",
                    "config_id": 135043,
                    "id": 13637492,
                    "label": "ds-man-02",
                    "mode": "accept",
                    "nodebalancer_id": 110572,
                    "status": "UP",
                    "weight": 2
                },
                {
                    "address": "192.168.130.46:8443",
                    "config_id": 135043,
                    "id": 13637501,
                    "label": "ds-man-03",
                    "mode": "accept",
                    "nodebalancer_id": 110572,
                    "status": "Unknown",
                    "weight": 3
                }
            ],
            "nodes_status": {
                "down": 4,
                "up": 0
            },
            "port": 80,
            "protocol": "http",
            "proxy_protocol": "none",
            "ssl_cert": null,
            "ssl_commonname": "",
            "ssl_fingerprint": "",
            "ssl_key": null,
            "stickiness": "table"
        }
    ],
    "created": "2020-12-27T17:38:50",
    "hostname": "nb-192-46-238-203.frankfurt.nodebalancer.linode.com",
    "id": 110572,
    "ipv4": "192.46.238.203",
    "ipv6": "2a01:7e01:1::c02e:eecb",
    "label": "test-lb-1",
    "region": "eu-central",
    "tags": [],
    "transfer": {
        "in": 0.10416603088378906,
        "out": 0.01116180419921875,
        "total": 0.11532783508300781
    },
    "updated": "2020-12-27T17:38:50"
  }
'''


def main():
    AnsibleModule(dict()).fail_json('balancer is action')


if __name__ == '__main__':
    main()
