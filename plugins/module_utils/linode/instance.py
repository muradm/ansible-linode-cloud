# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from datetime import datetime
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed


def instance_find(client, label):
    from linode_api4 import Instance

    try:
        return client.linode.instances(Instance.label == label)[0]
    except IndexError:
        return None
    except Exception as e:
        linode_raise_client_error(e)


def instance_create(client, args, check_mode=False):
    non_optional = ['region', 'type', 'image', 'label', 'authorized_keys']
    remaining = _filter_dict_keys(args, non_optional)

    try:
        if not check_mode:
            response = client.linode.instance_create(
                ltype=args['type'],
                region=args['region'],
                image=args['image'],
                authorized_keys=args['authorized_keys'],
                label=args['label'],
                **remaining
            )

            if isinstance(response, tuple):
                instance, root_pass = response
                result = deepcopy(instance._raw_json)
                result['root_pass'] = root_pass
            else:
                instance = response
                result = deepcopy(instance._raw_json)

            if 'ipv4_public_rdns' in args:
                instance.ips.ipv4.public[0].rdns = '' if not args['ipv4_public_rdns'] else args['ipv4_public_rdns']
                instance.ips.ipv4.public[0].rdns.save()

        else:
            result = _fake_instance(args)

        return result

    except Exception as e:
        linode_raise_client_error(e)


def instance_update(client, instance, args, check_mode=False):
    result = deepcopy(instance._raw_json)
    updated = False

    try:
        updated = updated or _update_if_needed(
            instance, result, args, 'group', check_mode)
        updated = updated or _update_if_needed(
            instance, result, args, 'tags', check_mode, to_be_sorted=True)

        if updated and not check_mode:
            instance.save()

        if 'private_ip' in args and args['private_ip']:
            if len(instance.ips.ipv4.private) == 0:
                updated = True
                if not check_mode:
                    client.networking.ip_allocate(instance, public=False)

        if 'ipv4_public_rdns' in args:
            cur = instance.ips.ipv4.public[0].rdns
            if cur != args['ipv4_public_rdns']:
                updated = True
                if not check_mode:
                    instance.ips.ipv4.public[0].rdns = '' if not args['ipv4_public_rdns'] else args['ipv4_public_rdns']
                    instance.ips.ipv4.public[0].rdns.save()

        return (updated, result)

    except Exception as e:
        linode_raise_client_error(e)


def instance_remove(instance, check_mode=False):
    try:
        if not check_mode:
            instance.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _fake_instance(args):
    return {
        'alerts': {},
        'backups': {},
        'created': datetime.now().isoformat(),
        'hypervisor': 'kvm',
        'id': -1,
        'ipv4': ["0.0.0.0"],
        'ipv6': '0000:0000::0000:0000:0000:0000/64',
        'root_pass': 'check_mode' if 'root_pass' not in args else args['root_pass'],
        'specs': {},
        'status': 'provisioning',
        'updated': datetime.now().isoformat(),
        'watchdog_enabled': True,
        'region': args['region'],
        'ltype': args['type'],
        'image': args['image'],
        'label': args['label'],
        'group': '' if 'group' not in args else args['group'],
        'tags': [] if 'tags' not in args else args['tags'],
        'authorized_keys': args['authorized_keys'],
    }
