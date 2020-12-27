# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from datetime import datetime
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed


def balancer_find(client, label):
    from linode_api4 import NodeBalancer

    try:
        return client.domains(NodeBalancer.label == label)[0]
    except IndexError:
        return None
    except Exception as e:
        linode_raise_client_error(e)


def balancer_create(client, args, check_mode=False):
    return {}


def balancer_update(client, balancer, args, check_mode=False):
    return (False, {})


def balancer_remove(client, balancer, check_mode=False):
    try:
        if not check_mode:
            balancer.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)
