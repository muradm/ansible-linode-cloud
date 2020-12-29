# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from datetime import datetime
from .domain_record import domain_record_create, domain_record_update, domain_record_remove, domain_record_match
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed


def domain_find(client, domain):
    from linode_api4 import Domain

    try:
        return client.domains(Domain.domain == domain)[0]
    except IndexError:
        return None
    except Exception as e:
        linode_raise_client_error(e)


def domain_create(client, args, check_mode=False):
    non_optional = ['domain', 'type', 'records']
    remaining = _filter_dict_keys(args, non_optional)

    try:
        if not check_mode:
            domain = client.domain_create(
                args['domain'], args['type'] == 'master', **remaining)
            result = deepcopy(domain._raw_json)
        else:
            domain = None
            result = _fake_domain(args)

        result['records'] = []
        if 'records' in args:
            for rec in args['records']:
                result['records'].append(
                    domain_record_create(domain, rec, check_mode))

        return result

    except Exception as e:
        linode_raise_client_error(e)


def domain_update(domain, args, check_mode=False):
    result = deepcopy(domain._raw_json)
    updated = False

    try:
        for f in [
            'soa_email', 'group', 'description',
            'retry_sec', 'expire_sec', 'refresh_sec', 'ttl_sec'
        ]:
            updated = updated or _update_if_needed(
                domain, result, args, f, check_mode)

        for f in ['tags', 'master_ips', 'axfr_ips']:
            updated = updated or _update_if_needed(
                domain, result, args, f, check_mode, to_be_sorted=True)

        if updated and not check_mode:
            domain.save()

        if 'records' in args:
            keep_unknown_records = args['keep_unknown_records'] if 'keep_unknown_records' in args else True
            return_unknown_records = args['return_unknown_records'] if 'return_unknown_records' in args else False
            drecords = domain.records
            arecords = args['records']
            rrecords = []

            for drec in drecords:
                if not _domain_record_configured(drec, arecords):
                    if not keep_unknown_records:
                        domain_record_remove(drec, check_mode)
                        updated = True
                    elif return_unknown_records:
                        rrecords.append(drec._raw_json)
                else:
                    for arec in arecords:
                        if domain_record_match(drec, arec):
                            upd, rec = domain_record_update(
                                drec, arec, check_mode)
                            rrecords.append(rec)
                            updated = updated or upd
                            break

            for arec in arecords:
                if _domain_record_new(arec, rrecords):
                    rrecords.append(domain_record_create(
                        domain, arec, check_mode))
                    updated = True

            result['records'] = rrecords

        return (updated, result)

    except Exception as e:
        linode_raise_client_error(e)


def domain_remove(domain, check_mode=False):
    try:
        if not check_mode:
            domain.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _domain_record_configured(drec, records):
    for r in records:
        if domain_record_match(drec, r):
            return True
    return False


def _domain_record_new(arec, records):
    for r in records:
        if domain_record_match(r, arec):
            return False
    return True


def _fake_domain(args):
    return {
        'axfr_ips': args['axfr_ips'],
        'created': datetime.now().isoformat(),
        'description': args['description'] if 'description' in args else '',
        'expire_sec': args['expire_sec'] if 'expire_sec' in args else 0,
        'group': args['group'] if 'group' in args else '',
        'id': -1,
        'master_ips': args['master_ips'],
        'refresh_sec': args['refresh_sec'] if 'refresh_sec' in args else 0,
        'retry_sec': args['retry_sec'] if 'retry_sec' in args else 0,
        'soa_email': args['soa_email'] if 'soa_email' in args else '',
        'status': 'creating',
        'ttl_sec': args['ttl_sec'] if 'ttl_sec' in args else 0,
        'type': args['type'],
        'tags': [] if 'tags' not in args else args['tags'],
        'updated': datetime.now().isoformat(),
    }
