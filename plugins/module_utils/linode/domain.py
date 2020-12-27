# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from datetime import datetime
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed


def domain_record_find(client, domain, rtype, name, target):
    try:
        for drec in domain.records:
            if _domain_record_match_triplet({
                'type': drec.type,
                'name': drec.name,
                'target': drec.target,
            }, {
                'type': rtype,
                'name': name,
                'target': target,
            }):
                return drec
    except IndexError:
        return None
    except Exception as e:
        linode_raise_client_error(e)


def domain_record_create(client, domain, args, check_mode=False):
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


def domain_record_update(client, record, args, check_mode=False):
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


def domain_record_remove(client, record, check_mode=False):
    try:
        if not check_mode:
            record.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


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
            result = _fake_domain(args)

        if 'records' in args:
            result_records = []
            for rec in args['records']:
                result_records.append(
                    domain_record_create(client, domain, rec, check_mode))

            result['records'] = result_records

        return result

    except Exception as e:
        linode_raise_client_error(e)


def domain_update(client, domain, args, check_mode=False):
    result = deepcopy(domain._raw_json)
    updated = False

    try:
        updated = updated or _update_if_needed(
            domain, result, args, 'soa_email', check_mode)
        updated = updated or _update_if_needed(
            domain, result, args, 'group', check_mode)
        updated = updated or _update_if_needed(
            domain, result, args, 'description', check_mode)
        updated = updated or _update_if_needed(
            domain, result, args, 'retry_sec', check_mode)
        updated = updated or _update_if_needed(
            domain, result, args, 'expire_sec', check_mode)
        updated = updated or _update_if_needed(
            domain, result, args, 'refresh_sec', check_mode)
        updated = updated or _update_if_needed(
            domain, result, args, 'ttl_sec', check_mode)
        updated = updated or _update_if_needed(
            domain, result, args, 'tags', check_mode, to_be_sorted=True)
        updated = updated or _update_if_needed(
            domain, result, args, 'master_ips', check_mode, to_be_sorted=True)
        updated = updated or _update_if_needed(
            domain, result, args, 'axfr_ips', check_mode, to_be_sorted=True)

        if updated and not check_mode:
            domain.save()

        # here we need complex logic to find what records are changed and
        # how, from linode perspective they have id of record, from ansible
        # user perspective, there is no id, currently considering that
        # type,name,target triplet provides enough distinction for records
        # this will basically, for "changed" target (let's say A record's
        # hostname) we will intentionally remove old record first, and
        # then create new one
        if 'records' in args:
            result_records = []

            # touch linode_api4 objects once and only once
            for drec in domain.records:
                if not _domain_record_configured(drec, args['records']):
                    # if keep_unknown_records explicitly set, first remove remote
                    # records that we don't have
                    if 'keep_unknown_records' in args and not args['keep_unknown_records']:
                        domain_record_remove(client, drec, check_mode)
                        updated = True
                    elif 'return_unknown_records' in args and args['return_unknown_records']:
                        result_records.append(drec._raw_json)
                else:
                    # now for every configured and remotely existing record check
                    # if update required, note since we don't sync after removal above
                    # record should be checked again if it is configured, no harm
                    for arec in args['records']:
                        if _domain_record_requires_update(drec, arec):
                            upd, rec = domain_record_update(
                                client, drec, arec, check_mode)
                            result_records.append(rec)
                            updated = updated or upd
                        else:
                            result_records.append(drec._raw_json)

            # now we may have new records which remote does not have
            for arec in args['records']:
                if _domain_record_new(arec, result_records):
                    result_records.append(
                        domain_record_create(client, domain, arec, check_mode))
                    updated = True

            result['records'] = result_records

        return (updated, result)

    except Exception as e:
        linode_raise_client_error(e)


def domain_remove(client, domain, check_mode=False):
    try:
        if not check_mode:
            domain.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _domain_record_match_triplet(arec, brec):
    if str(arec['target']).lower() == str(brec['target']).lower():
        if str(arec['name']).lower() == str(brec['name']).lower():
            if str(arec['type']).lower() == str(brec['type']).lower():
                return True
    return False


def _domain_record_configured(drec, records):
    for r in records:
        if _domain_record_match_triplet({
            'type': drec.type,
            'name': drec.name,
            'target': drec.target,
        }, r):
            return True
    return False


def _domain_record_new(arec, records):
    for r in records:
        if _domain_record_match_triplet(r, arec):
            return False
    return True


def _domain_record_requires_update(drec, arec):
    if str(drec.type).lower() != str(arec['type']).lower():
        return False

    if str(drec.name).lower() != str(arec['name']).lower():
        return False

    if str(drec.target).lower() != str(arec['target']).lower():
        return False

    if 'ttl_sec' in arec and drec.ttl_sec != arec['ttl_sec']:
        return True

    if str(drec.type).lower() == 'mx':
        if 'priority' in arec and drec.priority != arec['priority']:
            return True

    elif str(drec.type).lower() == 'srv':
        if 'service' in arec and str(drec.service).lower() != str(arec['service']).lower():
            return True

        if 'protocol' in arec and str(drec.protocol).lower() != str(arec['protocol']).lower():
            return True

        if 'priority' in arec and drec.priority != arec['priority']:
            return True

        if 'weight' in arec and drec.weight != arec['weight']:
            return True

        if 'port' in arec and drec.port != arec['port']:
            return True

    elif str(drec.type).lower() == 'caa':
        if 'tag' in arec and str(drec.tag).lower() != str(arec['tag']).lower():
            return True

    return False


def _fake_domain(configured):
    return {
        'axfr_ips': configured['axfr_ips'],
        'created': datetime.now().isoformat(),
        'description': configured['description'] if 'description' in configured else '',
        'expire_sec': configured['expire_sec'] if 'expire_sec' in configured else 0,
        'group': configured['group'] if 'group' in configured else '',
        'id': -1,
        'master_ips': configured['master_ips'],
        'refresh_sec': configured['refresh_sec'] if 'refresh_sec' in configured else 0,
        'retry_sec': configured['retry_sec'] if 'retry_sec' in configured else 0,
        'soa_email': configured['soa_email'] if 'soa_email' in configured else '',
        'status': 'creating',
        'ttl_sec': configured['ttl_sec'] if 'ttl_sec' in configured else 0,
        'type': configured['type'],
        'tags': [] if 'tags' not in configured else configured['tags'],
        'updated': datetime.now().isoformat(),
    }


def _fake_domain_record(configured):
    return {
        'created': datetime.now().isoformat(),
        'id': -1,
        'name': configured['name'],
        'port': configured['port'] if 'port' in configured else 0,
        'priority': configured['priority'] if 'priority' in configured else 0,
        'protocol': configured['protocol'] if 'protocol' in configured else None,
        'service': configured['service'] if 'service' in configured else None,
        'tag': configured['tag'] if 'tag' in configured else None,
        'target': configured['target'],
        'ttl_sec': configured['ttl_sec'] if 'ttl_sec' in configured else 0,
        'type': configured['type'],
        'weight': configured['weight'] if 'weight' in configured else 0,
        'updated': datetime.now().isoformat(),
    }
