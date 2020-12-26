# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
action: domain_record
short_description: Create/update/remove a domain record in linode domain
description:
    - Uses I(type), I(name) and I(target) as key to identify record in I(domain)
options:
  state:
    description:
      - C(present) to create new or manage existing domain record
      - C(absent) to remove existing domain record
    choices: [ "present", "absent" ]
    default: "present"
    type: str
  domain:
    description: Domain this record should belong to.
    type: str
    required: true
  type:
    description:
        The type of Record this is in the DNS system. For example, A records associate
        a domain name with an IPv4 address, and AAAA records associate a domain name
        with an IPv6 address.
    choices: [ "A", "AAAA", "NS", "MX", "CNAME", "TXT", "SRV", "PTR", "CAA" ]
    type: str
    required: true
  name:
    description:
        The name of this Record. This field’s actual usage depends on the type of record
        this represents. For A and AAAA records, this is the subdomain being associated
        with an IP address etc. For '@' should be explicit empty string.
    type: str
    required: true
  target:
    description:
        The target for this Record. This field’s actual usage depends on the type of record
        this represents. For A and AAAA records, this is the address the named Domain
        should resolve to. With the exception of A and AAAA records, this field accepts
        a trailing period.
    type: str
    reqired: true
  ttl_sec:
    description:
        The amount of time in seconds that this Domain’s records may be cached by resolvers
        or other domain servers. Valid values are 300, 3600, 7200, 14400, 28800, 57600,
        86400, 172800, 345600, 604800, 1209600, and 2419200 - any other value will be
        rounded to the nearest valid value.
    type: int
    required: false
  priority:
    description:
        The priority of the target host in the range 0..255. Lower values are preferred.
    type: int
    required: false
  service:
    description:
        The service this Record identified. Only valid for SRV records.
    type: str
    reqired: false
  protocol:
    description:
        The protocol this Record’s service communicates with. Only valid for SRV records.
    type: str
    reqired: false
  weight:
    description:
        The relative weight of this Record in the range 0..65535. Higher values are preferred.
    type: int
    required: false
  port:
    description:
        The port this Record points to 0..65535.
    type: int
    required: false
  tag:
    description:
        The tag portion of a CAA record. It is invalid to set this on other record types.
    type: str
    reqired: false

requirements: [ "linode_api4", "cerberus" ]
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
- hosts: localhost
  connection: local
  tasks:
    - name: create A record in my-domain.com
      muradm.linode.domain_record:
        domain: my-domain.com
        type: A
        name: host1
        target: '1.1.1.5'
        ttl_sec: 300
        state: present

- hosts: localhost
  connection: local
  tasks:
    - name: delete A record in my-domain.com
      muradm.linode.domain_record:
        domain: my-domain.com
        type: A
        name: host1
        target: '1.1.1.5'
        state: absent
'''

RETURN = r'''
domain_record:
  description: The domain record description in JSON serialized form.
  returned: Always. When domain record deleted contains single field status with value deleted.
  type: dict
  sample: {
      "created": "2020-12-27T06:11:05",
      "id": 16814685,
      "name": "host2",
      "port": 0,
      "priority": 0,
      "protocol": null,
      "service": null,
      "tag": null,
      "target": "1.1.1.5",
      "ttl_sec": 0,
      "type": "A",
      "updated": "2020-12-27T06:11:05",
      "weight": 0
  }
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    AnsibleModule(dict()).fail_json('domain_record is action')


if __name__ == '__main__':
    main()
