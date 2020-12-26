# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
action: domain
short_description: Create/update/remove a linode domain
description:
    - Creates a linode domain if it does not exist and if I(state) is C(present) or removes domain
      if I(state) is C(absent).
    - Can create/update/remove I(records) in one go.
options:
  state:
    description:
      - C(present) to create new or manage existing linode domain
      - C(absent) to remote existing linode domain
    choices: [ "present", "absent" ]
    default: "present"
    type: str
  domain:
    description:
        The domain this Domain represents. Domain labels cannot be longer
        than 63 characters and must conform to RFC1035. Domains must be unique
        on Linode’s platform, including across different Linode accounts; there
        cannot be two Domains representing the same domain.
    type: str
    required: true
  type:
    description:
        Whether this Domain represents the authoritative source of information
        for the domain it describes C(master), or whether it is a read-only
        copy of a master C(slave).
    choices: [ "master", "slave" ]
    type: str
    required: true
  soa_email:
    description:
        Start of Authority email address. This is required for type master Domains.
    type: str
    required: false
  description:
    description:
        A 1..255 characters long description for this Domain. This is for display purposes only.
    type: str
    required: false
  group:
    description:
        A 1..50 characters long group this Domain belongs to. This is for display purposes only.
    type: str
    required: false
  expire_sec:
    description:
        The amount of time in seconds that may pass before this Domain is no longer
        authoritative. Valid values are 300, 3600, 7200, 14400, 28800, 57600, 86400,
        172800, 345600, 604800, 1209600, and 2419200 - any other value will be
        rounded to the nearest valid value.
    type: int
    required: false
  refresh_sec:
    description:
        The amount of time in seconds before this Domain should be refreshed. Valid
        values are 300, 3600, 7200, 14400, 28800, 57600, 86400, 172800, 345600, 604800,
        1209600, and 2419200 - any other value will be rounded to the nearest valid value.
    type: int
    required: false
  retry_sec:
    description:
        The interval, in seconds, at which a failed refresh should be retried. Valid
        values are 300, 3600, 7200, 14400, 28800, 57600, 86400, 172800, 345600, 604800,
        1209600, and 2419200 - any other value will be rounded to the nearest valid value.
    type: int
    required: false
  ttl_sec:
    description:
        The amount of time in seconds that this Domain’s records may be cached by
        resolvers or other domain servers. Valid values are 0, 300, 3600, 7200, 14400,
        28800, 57600, 86400, 172800, 345600, 604800, 1209600, and 2419200 - any other
        value will be rounded to the nearest valid value. I(ttl_sec) will default to 0
        if no value is provided. A value of 0 is equivalent to a value of 86400.
    type: int
    required: false
  tags:
    description:
        An array of tags applied to this object. Tags are for organizational purposes only.
    type: list
    default: []
    elements: str
    reqired: false
  axfr_ips:
    description:
        The list of IPs that may perform a zone transfer for this Domain. This is
        potentially dangerous, and should be set to an empty list unless you intend to use it.
    type: list
    default: []
    elements: str
    reqired: false
  master_ips:
    description:
        The IP addresses representing the master DNS for this Domain. At least one value
        is required for I(type) C(slave) Domains.
    type: list
    default: []
    elements: str
    reqired: false
  records:
    description:
        List of domain records this domain should have. See domain_record action for
        available fields. See also I(keep_unknown_records) and I(return_unknown_records).
    type: list
    default: []
    required: false
  keep_unknown_records:
    description:
        When the value is C(True), which is default, will not touch remote records which
        are not listed in I(records) field. This is default behavior, and may cause side
        effects in such way that, removed records from ansible or I(type), I(name),
        I(target) updated records in asible will keep previous records in the domain.
        When set to C(False), remote domain will have exactly same list of records as
        expressed in I(records), i.e. records which are not listed in this field will
        be actually removed from domain.
    type: bool
    required: false
    default: true
  return_unknown_records:
    description:
        When the value is C(False), which is default, will not return in result remote
        records which are not listed in I(records).
    type: bool
    required: false
    default: true
requirements: [ "linode_api4", "cerberus" ]
author:
- muradm (@muradm)
'''

EXAMPLES = r'''
# maintain my-domain.com so that it has two records, since keep_unknown_records is
# true and return_unknown_records is false by default, in the cloud there might be
# more records
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.domain:
        domain: my-domain.com
        type: master
        soa_email: admin@my-domain.com
        records:
          - { type: A, name: 'host1', target: '1.1.1.4', ttl_sec: 300 }
          - { type: MX, name: '', target: 'host1.my-domain.com', ttl_sec: 300 }

# the same as above, but domain will have exactly two records
- hosts: localhost
  connection: local
  tasks:
    - muradm.linode.domain:
        domain: my-domain.com
        type: master
        soa_email: admin@my-domain.com
        keep_unknown_records: false
        records:
          - { type: A, name: 'host1', target: '1.1.1.4', ttl_sec: 300 }
          - { type: MX, name: '', target: 'host1.my-domain.com', ttl_sec: 300 }

- name: remove my domain
  hosts: localhost
  tasks:
  - muradm.linode.domain:
      name: 'my-domain.com'
      state: 'absent'
'''

RETURN = r'''
domain:
  description: The domain description in JSON serialized form.
  returned: Always. When domain deleted contains single field status with value deleted.
  type: dict
  sample: {
      "axfr_ips": [],
      "created": "2020-12-27T06:08:33",
      "description": "",
      "domain": "my-domain.com",
      "expire_sec": 0,
      "group": "",
      "id": 1501410,
      "master_ips": [],
      "records": [
          {
              "created": "2020-12-27T06:08:35",
              "id": 16814671,
              "name": "",
              "port": 0,
              "priority": 0,
              "protocol": null,
              "service": null,
              "tag": null,
              "target": "host1.my-domain.com",
              "ttl_sec": 300,
              "type": "MX",
              "updated": "2020-12-27T06:08:35",
              "weight": 0
          },
          {
              "created": "2020-12-27T06:08:35",
              "id": 16814670,
              "name": "host1",
              "port": 0,
              "priority": 0,
              "protocol": null,
              "service": null,
              "tag": null,
              "target": "1.1.1.4",
              "ttl_sec": 300,
              "type": "A",
              "updated": "2020-12-27T06:08:35",
              "weight": 0
          }
      ],
      "refresh_sec": 0,
      "retry_sec": 0,
      "soa_email": "admin@my-domain.com",
      "status": "active",
      "tags": [],
      "ttl_sec": 0,
      "type": "master",
      "updated": "2020-12-27T06:08:35"
  }
'''


def main():
    AnsibleModule(dict()).fail_json('domain is action')


if __name__ == '__main__':
    main()
