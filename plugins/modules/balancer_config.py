# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
action: balancer_config
short_description: Create/update/remove a linode balancer config
description:
    - Action will query by I(balancer) and I(port) existing cloud state.
    - Fails with AnsibleError if specified I(balancer) does exist 
    - Linode internal IDs are not used to perform operations, thus updating I(balancer) and I(port)
      here impossible, you will be referring to another balancer configuration. Other fields
      are updatable here.
options:
  state:
    description:
      - C(present) to create new or manage existing linode balancer config
      - C(absent) to remote existing linode balancer config
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
        The port this config is for. These values must be unique across configs on a single
        balancer, i.e. you can’t have two configs for port 80, for example. While some ports imply some
        protocols, no enforcement is done and you may configure your balancer however is useful to you.
        For example, while port 443 is generally used for HTTPS, you do not need SSL configured to
        have a balancer listening on port 443.
    type: int
    required: true
  protocol:
    description:
        The protocol this port is configured to serve. For C(http) and C(tcp), I(ssl_cert) and I(ssl_key)
        are not supported.
    choices: [ "http", "https", "tcp" ]
    type: str
    required: true
  label:
    description:
        A 3..32 characters long label for this node. This is for display purposes only.
    type: str
    required: true
  algorithm:
    description:
        What algorithm this balancer should use for routing traffic to backends.
    choices: [ "roundrobin", "leastconn", "source" ]
    type: str
    required: true
  stickiness:
    description:
        Controls how session stickiness is handled on this port.
        - If set to C(none) connections will always be assigned a backend based on the algorithm configured.
        - If set to C(table) sessions from the same remote address will be routed to the same backend.
        - For HTTP or HTTPS clients, C(http_cookie) allows sessions to be routed to the same backend based
          on a cookie set by the balancer.
    choices: [ "none", "table", "http_cookie" ]
    type: str
    required: true
  proxy_protocol:
    description:
        ProxyProtocol is a TCP extension that sends initial TCP connection information such as source/destination
        IPs and ports to backend devices. This information would be lost otherwise. Backend devices must be
        configured to work with ProxyProtocol if enabled.
        - If set to none, the balancer doesn’t send any auxilary data over TCP connections. This is the default.
        - If set to C(v1), the human-readable header format Version 1 is used.
        - If set to C(v2), the binary header format Version 2 is used.
    choices: [ "none", "v1", "v2" ]
    type: str
    required: true
    default: "none"
  ssl_cert:
    description:
        The PEM-formatted public SSL certificate or the combined PEM-formatted SSL certificate and Certificate
        Authority chain, that should be served on this NodeBalancerConfig’s port.
        The contents of this field will not be shown in any responses that display the NodeBalancerConfig. Instead,
        <REDACTED> will be printed where the field appears.
        The read-only I(ssl_commonname) and I(ssl_fingerprint) fields in a NodeBalancerConfig response are
        automatically derived from your certificate. Please refer to these fields to verify that the appropriate
        certificate was assigned to your NodeBalancerConfig.
    type: str
    required: false
  ssl_key:
    description:
        The PEM-formatted private key for the SSL certificate set in the I(ssl_cert) field.
        The contents of this field will not be shown in any responses that display the NodeBalancerConfig. Instead,
        <REDACTED> will be printed where the field appears.
        The read-only I(ssl_commonname) and I(ssl_fingerprint) fields in a NodeBalancerConfig response are
        automatically derived from your certificate. Please refer to these fields to verify that the appropriate
        certificate was assigned to your NodeBalancerConfig.
    type: str
    required: false
  cipher_suite:
    description:
        What ciphers to use for SSL connections served by this NodeBalancer. C(legacy) is considered insecure and
        should only be used if necessary.
    choices: [ "recommended", "legacy" ]
    type: str
    required: true
    default: "recommended"
  check_passive:
    description:
        If C(True), any response from this backend with a B(5xx) status code will be enough for it to be considered
        unhealthy and taken out of rotation.
    type: bool
    required: false
    default: true
  check_interval:
    description:
        How often, in seconds, to check that backends are up and serving requests.
    type: int
    required: false
    default: 0
  check_timeout:
    description:
        How long, in seconds, to wait for a check attempt before considering it failed. In the range 1..30.
    type: int
    required: false
    default: 30
  check_attempts:
    description:
        How many times to attempt a check before considering a backend to be down. In the range 1..30.
    type: int
    required: false
    default: 3
  check_path:
    description:
        The URL path to check on each backend. If the backend does not respond to this request it is considered to be down.
    type: str
    required: false
  check_body:
    description:
        This value must be present in the response body of the check in order for it to pass. If this value
        is not present in the response body of a check request, the backend is considered to be down.
    type: str
    required: false
  nodes:
    description:
        Nodes that should be configured by this configuration. For the fields refer to B(balancer_node) action. Also
        see related I(keep_unknown_nodes) and I(return_unknown_nodes).
    type: list
    required: false
    default: []
  keep_unknown_nodes:
    description:
        When managing configuration using this action, if I(nodes) field is not configured, but nodes actually configured
        elsewhere, this should remain C(True). When set to C(False), B(balancer_config) action will consider I(nodes)
        an exhaustive list of nodes that should be configured under this configuration. Thus, if I(nodes) is empty,
        B(balancer_config) action will also empty the configuration in the cloud.
    type: bool
    required: false
    default: true
  return_unknown_nodes:
    description:
        When partially or not managing I(nodes) by this action, if this is set to C(True), result will include
        the nodes configured elsewhere, otherwise returns will include only nodes listed in I(nodes).
    type: bool
    required: false
    default: false
requirements: [ "linode_api4", "cerberus" ]
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
# control single balancer configuration
# test-lb-1 balancer should be performed elsewhere
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer_config:
        balancer: test-lb-1
        port: 80
        protocol: http
        algorithm: roundrobin
        stickiness: table
        return_unknown_nodes: true # if some nodes configured elsewhere, result will include them

# ensure that this confiration is configured as set here
# and has 2 nodes (may be more nodes, if other configured elsewhere)
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer_config:
        balancer: test-lb-1
        port: 80
        protocol: http
        algorithm: roundrobin
        stickiness: table
        nodes: [
            { address: '192.168.153.123:8080', label: 'ds-man-01', mode: 'accept', weight: 1 },
            { address: '192.168.161.168:8080', label: 'ds-man-02', mode: 'accept', weight: 2 },
        ]

# ensure that this confiration is configured as set here
# and has exactly 2 nodes as specified here (othernodes configured from elsewhere
# will be effectively removed)
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer_config:
        balancer: test-lb-1
        port: 80
        protocol: http
        algorithm: roundrobin
        stickiness: table
        keep_unknown_nodes: false
        nodes: [
            { address: '192.168.153.123:8080', label: 'ds-man-01', mode: 'accept', weight: 1 },
            { address: '192.168.161.168:8080', label: 'ds-man-02', mode: 'accept', weight: 2 },
        ]

# below configuration will make sure that no nodes configured
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer_config:
        balancer: test-lb-1
        port: 80
        protocol: http
        algorithm: roundrobin
        stickiness: table
        keep_unknown_nodes: false

# remove this configuration completely
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.balancer_config:
        balancer: test-lb-1
        port: 80
        state: absent
'''

RETURN = r'''
balancer_config:
  description: The balancer config description in JSON serialized form.
  returned: Always. When balancer config deleted contains single field status with value deleted.
  type: dict
  sample: {
    "algorithm": "roundrobin",
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
            "status": "DOWN",
            "weight": 1
        },
        {
            "address": "192.168.161.168:8080",
            "config_id": 135043,
            "id": 13637492,
            "label": "ds-man-02",
            "mode": "accept",
            "nodebalancer_id": 110572,
            "status": "DOWN",
            "weight": 2
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
'''


def main():
    AnsibleModule(dict()).fail_json('balancer_config is action')


if __name__ == '__main__':
    main()
