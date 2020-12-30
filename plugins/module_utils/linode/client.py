# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.module_utils.ansible_release import __version__ as ansible_version
from os import environ
from time import sleep

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

def linode_wait_for_status(obj, status, timeout=600):
    if not hasattr(obj, 'status'):
        raise AnsibleError(u'cannot wait for object without status: %s' % str(obj))

    waited = 0
    wait_by = 10
    while obj.status != status:
        sleep(wait_by)
        waited = waited + wait_by
        if waited > timeout and obj.status != status:
            raise AnsibleError(u'%s status wait timeout for: %s' % (status, str(obj)))

def linode_wait_for_status_changed(obj, current_status, timeout=600):
    if not hasattr(obj, 'status'):
        raise AnsibleError(u'cannot wait for object without status: %s' % str(obj))

    waited = 0
    wait_by = 10
    while obj.status == current_status:
        sleep(wait_by)
        waited = waited + wait_by
        if waited > timeout and obj.status == current_status:
            raise AnsibleError(u'%s current status change wait timeout for: %s' % (current_status, str(obj)))
