# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from datetime import datetime
from .balancer_config import balancer_config_find, balancer_config_create, balancer_config_update, balancer_config_remove
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed


def balancer_find(client, label):
    from linode_api4 import NodeBalancer

    try:
        return client.nodebalancers(NodeBalancer.label == label)[0]
    except IndexError:
        return None
    except Exception as e:
        linode_raise_client_error(e)


def balancer_create(client, args, check_mode=False):
    non_optional = ['region']
    remaining = _filter_dict_keys(args, non_optional)

    try:
        if not check_mode:
            balancer = client.nodebalancer_create(args['region'], **remaining)
            result = deepcopy(balancer._raw_json)
            result['nodes'] = []

            if 'configs' in args:
                return_unknown_configs = args['return_unknown_configs'] if 'return_unknown_configs' in args else False
                cconfigs = balancer.configs
                aconfigs = args['configs'] if 'configs' in args else []
                rconfigs = []

                for cconfig in cconfigs:
                    appended = False
                    for aconfig in aconfigs:
                        if aconfig['port'] == cconfig.port:
                            rconfigs.append(cconfig._raw_json)
                            appended = True
                            break
                    if not appended and return_unknown_configs:
                        rconfigs.append(cconfig._raw_json)

                result['configs'] = rconfigs
        else:
            balancer = None
            result = _fake_balancer(args)
            result['configs'] = []

            if 'configs' in args:
                for aconfig in args['configs']:
                    result['configs'].append(balancer_config_create(
                        balancer, aconfig, check_mode))

        if 'ipv4_public_rdns' in args and not check_mode:
            balancer.ipv4.rdns = '' if not args['ipv4_public_rdns'] else args['ipv4_public_rdns']
            balancer.ipv4.save()

        return result

    except Exception as e:
        linode_raise_client_error(e)


def balancer_update(client, balancer, args, check_mode=False):
    result = deepcopy(balancer._raw_json)
    updated = False

    try:
        updated = updated or _update_if_needed(
            balancer, result, args, 'client_conn_throttle', check_mode)

        # AttributeError: 'NodeBalancer' object has no attribute 'tags'
        # updated = updated or _update_if_needed(
        #     balancer, result, args, 'tags', check_mode, to_be_sorted=True)

        if updated and not check_mode:
            balancer.save()

        if 'configs' in args:
            keep_unknown_configs = args['keep_unknown_configs'] if 'keep_unknown_configs' in args else False
            return_unknown_configs = args['return_unknown_configs'] if 'return_unknown_configs' in args else False
            aconfigs = args['configs']
            cconfigs = balancer.configs
            rconfigs = []

            for cconfig in cconfigs:
                if not _is_config_configured(cconfig, aconfigs):
                    if not keep_unknown_configs:
                        balancer_config_remove(cconfig, check_mode)
                    elif return_unknown_configs:
                        rconfigs.append(cconfig._raw_json)
                else:
                    for aconfig in aconfigs:
                        if cconfig.port == aconfig['port']:
                            upd, config = balancer_config_update(
                                cconfig, aconfig, check_mode)
                            rconfigs.append(config)
                            updated = updated or upd
                            break

            for aconfig in aconfigs:
                if _is_config_new(aconfig, rconfigs):
                    config = balancer_config_create(
                        balancer, aconfig, check_mode)
                    rconfigs.append(config)
                    updated = True

            result['configs'] = rconfigs

        if 'ipv4_public_rdns' in args:
            updated = True
            if not check_mode:
                balancer.ipv4.rdns = '' if not args['ipv4_public_rdns'] else args['ipv4_public_rdns']
                balancer.ipv4.save()

        return (updated, result)
    except Exception as e:
        linode_raise_client_error(e)


def balancer_remove(client, balancer, check_mode=False):
    try:
        if not check_mode:
            balancer.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _is_config_configured(cconfig, aconfigs):
    for aconfig in aconfigs:
        if aconfig['port'] == cconfig.port:
            return True
    return False


def _is_config_new(aconfig, rconfigs):
    for rconfig in rconfigs:
        if rconfig['port'] == aconfig['port']:
            return False
    return True


def _fake_balancer(args):
    return {
        "client_conn_throttle": args['client_conn_throttle'] if 'client_conn_throttle' in args else 0,
        'created': datetime.now().isoformat(),
        "hostname": "nb-0-0-0-0.frankfurt.nodebalancer.linode.com",
        "id": -1,
        "ipv4": "0.0.0.0",
        'ipv6': '0000:0000::0000:0000:0000:0000/64',
        "label": args['label'],
        "region": args['region'],
        "tags": [],
        "transfer": {
            "in": None,
            "out": None,
            "total": None
        },
        'updated': datetime.now().isoformat(),
    }
