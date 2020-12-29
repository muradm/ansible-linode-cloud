# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from datetime import datetime
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed, objview


def domain_record_match(_a, _b):
    a = objview(_a) if isinstance(_a, dict) else _a
    b = objview(_b) if isinstance(_b, dict) else _b

    def _get(v, f):
        return getattr(v, f)

    def _is_same(a, b, f, to_lower=False):
        _afv = getattr(a, f)
        _bfv = getattr(b, f)

        if _afv is None or _bfv is None:
            return False

        if to_lower:
            _afv = str(_afv).lower()
            _bfv = str(_bfv).lower()

        return _afv == _bfv

    def _are_same(a, b, ff):
        return all(map(lambda f: _is_same(a, b, f), ff))

    if not _is_same(a, b, 'type', to_lower=True):
        return False

    if str(getattr(a, 'type')).lower() == 'srv':
        return _are_same(a, b, ['target', 'service', 'protocol', 'port'])

    return _are_same(a, b, ['name', 'target'])


def domain_record_find(domain, arec):
    try:
        for record in domain.records:
            if domain_record_match(record, arec):
                return record

        return None
    except Exception as e:
        linode_raise_client_error(e)


def domain_record_create(domain, args, check_mode=False):
    non_optional = ['type']
    remaining = _filter_dict_keys(args, non_optional)

    try:
        if not check_mode:
            record = domain.record_create(args['type'], **remaining)
            result = deepcopy(record._raw_json)
        else:
            result = _fake_domain_record(args)

        return result

    except Exception as e:
        linode_raise_client_error(e)


def domain_record_update(record, args, check_mode=False):
    result = deepcopy(record._raw_json)
    updated = False

    try:
        updated = updated or _update_if_needed(
            record, result, args, 'ttl_sec', check_mode)

        if str(record.type).lower() == 'mx':
            updated = updated or _update_if_needed(
                record, result, args, 'priority', check_mode)

        if str(record.type).lower() == 'srv':
            updated = updated or _update_if_needed(
                record, result, args, 'service', check_mode, to_be_lower=True)
            updated = updated or _update_if_needed(
                record, result, args, 'protocol', check_mode, to_be_lower=True)
            updated = updated or _update_if_needed(
                record, result, args, 'priority', check_mode)
            updated = updated or _update_if_needed(
                record, result, args, 'weight', check_mode)
            updated = updated or _update_if_needed(
                record, result, args, 'port', check_mode)

        if str(record.type).lower() == 'caa':
            updated = updated or _update_if_needed(
                record, result, args, 'tag', check_mode, to_be_lower=True)

        if updated and not check_mode:
            record.save()

        return (updated, result)
    except Exception as e:
        linode_raise_client_error(e)


def domain_record_remove(record, check_mode=False):
    try:
        if not check_mode:
            record.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _fake_domain_record(args):
    return {
        'created': datetime.now().isoformat(),
        'id': -1,
        'name': args['name'],
        'port': args['port'] if 'port' in args else 0,
        'priority': args['priority'] if 'priority' in args else 0,
        'protocol': args['protocol'] if 'protocol' in args else None,
        'service': args['service'] if 'service' in args else None,
        'tag': args['tag'] if 'tag' in args else None,
        'target': args['target'],
        'ttl_sec': args['ttl_sec'] if 'ttl_sec' in args else 0,
        'type': args['type'],
        'weight': args['weight'] if 'weight' in args else 0,
        'updated': datetime.now().isoformat(),
    }
