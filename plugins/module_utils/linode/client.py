# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.module_utils.ansible_release import __version__ as ansible_version
from os import environ


def linode_client(args, vars, env=environ):
    try:
        from linode_api4 import LinodeClient
    except ImportError:
        raise AnsibleError(u'could not import linode_api4 module')

    at = args.get(
        'access_token',
        vars.get(
            'linode_access_token',
            env.get('LINODE_ACCESS_TOKEN', None)
        )
    )

    if at is None:
        raise AnsibleError(u'could not resolve linode access token')

    user_agent = 'Ansible-linode_api4/%s' % ansible_version

    return LinodeClient(at, user_agent=user_agent)
