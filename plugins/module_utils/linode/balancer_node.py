# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from datetime import datetime
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed


def balancer_node_find(config, address):
    try:
        for node in config.nodes:
            if node.address == address:
                return node

        return None
    except Exception as e:
        linode_raise_client_error(e)


def balancer_node_create(config, args, check_mode=False):
    non_optional = ['address', 'label']
    remaining = _filter_dict_keys(args, non_optional)

    try:
        if not check_mode:
            node = config.node_create(
                label=args['label'],
                address=args['address'],
                **remaining
            )

            result = deepcopy(node._raw_json)
        else:
            result = _fake_balancer_node(args)

        return result

    except Exception as e:
        linode_raise_client_error(e)


def balancer_node_update(node, args, check_mode=False):
    result = deepcopy(node._raw_json)
    updated = False

    try:
        for f in ['label', 'mode', 'weight']:
            updated = updated or _update_if_needed(
                node, result, args, f, check_mode)

        if updated and not check_mode:
            node.save()

        return (updated, result)
    except Exception as e:
        linode_raise_client_error(e)


def balancer_node_remove(node, check_mode=False):
    try:
        if not check_mode:
            node.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _fake_balancer_node(args):
    return {
        "address": args['address'],
        "config_id": -1,
        "id": -1,
        "label": args['label'],
        "mode": args['mode'],
        "nodebalancer_id": -1,
        "status": "UP",
        "weight": args['weight']
    }
