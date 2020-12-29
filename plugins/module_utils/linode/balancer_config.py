# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from .balancer_node import balancer_node_create, balancer_node_update, balancer_node_remove
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed


def balancer_config_find(balancer, port):
    try:
        for config in balancer.configs:
            if config.port == port:
                return config

        return None
    except Exception as e:
        linode_raise_client_error(e)


def balancer_config_create(balancer, args, check_mode=False):
    non_optional = ['return_unknown_nodes', 'keep_unknown_nodes', 'nodes']
    remaining = _filter_dict_keys(args, non_optional)

    try:
        if not check_mode:
            config = balancer.config_create(label=None, **remaining)
            result = deepcopy(config._raw_json)
            result['nodes'] = []

        else:
            config = None
            result = _fake_balancer_config(args)
            result['nodes'] = []

        if 'nodes' in args:
            for anode in args['nodes']:
                node = balancer_node_create(config, anode, check_mode)
                result['nodes'].append(node)

        return result

    except Exception as e:
        linode_raise_client_error(e)


def balancer_config_update(config, args, check_mode=False):
    result = deepcopy(config._raw_json)
    updated = False

    try:
        for f in [
            'protocol', 'algorithm', 'stickiness', 'check',
            'check_passive', 'check_interval', 'check_timeout', 'check_attempts',
        ]:
            updated = updated or _update_if_needed(
                config, result, args, f, check_mode)

        effective_protocol = args['protocol'] if 'protocol' in args else config.protocol

        if effective_protocol == 'tcp':
            updated = updated or _update_if_needed(
                config, result, args, 'proxy_protocol', check_mode)

        if effective_protocol == 'https':
            for f in ['ssl_cert', 'ssl_key', 'cipher_suite']:
                updated = updated or _update_if_needed(
                    config, result, args, f, check_mode)

        effective_check = args['check'] if 'check' in args else config.protocol

        if effective_check in ['http', 'http_body']:
            updated = updated or _update_if_needed(
                config, result, args, 'check_path', check_mode)

        if effective_check == 'http_body':
            updated = updated or _update_if_needed(
                config, result, args, 'check_body', check_mode)

        if updated and not check_mode:
            config.save()

        if 'nodes' in args:
            keep_unknown_nodes = args['keep_unknown_nodes'] if 'keep_unknown_nodes' in args else True
            return_unknown_nodes = args['return_unknown_nodes'] if 'return_unknown_nodes' in args else False
            anodes = args['nodes']
            cnodes = config.nodes
            rnodes = []

            for cnode in cnodes:
                if not _is_node_configured(cnode, anodes):
                    if not keep_unknown_nodes:
                        balancer_node_remove(cnode, check_mode)
                        updated = True
                    elif return_unknown_nodes:
                        cnode.address  # touch node address, so that linode_api4 loads it
                        rnodes.append(cnode._raw_json)
                else:
                    for anode in anodes:
                        if cnode.address == anode['address']:
                            upd, node = balancer_node_update(
                                cnode, anode, check_mode)
                            rnodes.append(node)
                            updated = updated or upd
                            break

            for anode in anodes:
                if _is_node_new(anode, rnodes):
                    node = balancer_node_create(config, anode, check_mode)
                    rnodes.append(node)
                    updated = True

            result['nodes'] = rnodes

        return (updated, result)
    except Exception as e:
        linode_raise_client_error(e)


def balancer_config_remove(config, check_mode=False):
    try:
        if not check_mode:
            config.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _is_node_configured(cnode, anodes):
    for anode in anodes:
        if anode['address'] == cnode.address:
            return True
    return False


def _is_node_new(anode, rnodes):
    for rnode in rnodes:
        if rnode['address'] == anode['address']:
            return False
    return True


def _fake_balancer_config(args):
    return {
        "algorithm": args['algorithm'],
        "check": args['check'],
        "check_attempts": args['check_attempts'] if 'check_attempts' in args else 3,
        "check_body": args['check_body'] if 'check_body' in args else '',
        "check_interval": args['check_interval'] if 'check_interval' in args else 0,
        "check_passive": args['check_passive'] if 'check_passive' in args else True,
        "check_path": args['check_path'] if 'check_path' in args else '',
        "check_timeout": args['check_timeout'] if 'check_timeout' in args else 30,
        "cipher_suite": args['cipher_suite'],
        "id": -1,
        "nodebalancer_id": -1,
        "nodes_status": {
            "down": 0,
            "up": len(args['nodes'])
        },
        "port": 443,
        "protocol": args['protocol'],
        "proxy_protocol": args['proxy_protocol'],
        "ssl_cert": args['ssl_cert'] if 'ssl_cert' in args else None,
        "ssl_commonname": "",
        "ssl_fingerprint": "",
        "ssl_key": args['ssl_key'] if 'ssl_key' in args else None,
        "stickiness": args['stickiness']
    }
