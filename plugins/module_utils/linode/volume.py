# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from copy import deepcopy
from datetime import datetime
from .client import linode_wait_for_status
from .error import linode_raise_client_error
from .util import _filter_dict_keys, _update_if_needed
from .instance import instance_find


def volume_find(client, label):
    from linode_api4 import Volume

    try:
        return client.volumes(Volume.label == label)[0]
    except IndexError:
        return None
    except Exception as e:
        linode_raise_client_error(e)


def _ensure_attached_instance(client, args):
    if args['state'] != 'attached':
        return None

    if 'instance' not in args:
        raise AnsibleError(
            '%s volume set to be attached, but instance not specified' % args['label'])

    instance = instance_find(client, args['instance'])
    if instance is None:
        raise AnsibleError('no instance %s to create and attach %s volume' % (
            args['instance'], args['label']))

    return instance


def volume_create(client, args, check_mode=False):
    non_optional = ['region', 'size', 'label', 'instance']
    remaining = _filter_dict_keys(args, non_optional)

    try:
        instance = _ensure_attached_instance(client, args)

        if not check_mode:
            volume = client.volume_create(
                region=args['region'] if instance is None else instance.region,
                label=args['label'],
                size=args['size'],
                **remaining
            )

            linode_wait_for_status(instance, "active")

            if instance is not None:
                volume.attach(instance)

            result = deepcopy(volume._raw_json)
        else:
            result = _fake_volume(args)

        return result

    except Exception as e:
        linode_raise_client_error(e)


def volume_update(client, volume, args, check_mode=False):
    result = deepcopy(volume._raw_json)
    updated = False

    if volume.status != 'active':
        raise AnsibleError('%s volume has status of %s' %
                           (volume.label, volume.status))

    try:
        updated = updated or _update_if_needed(
            volume, result, args, 'tags', check_mode, to_be_sorted=True)

        if updated and not check_mode:
            volume.save()

        if args['state'] == 'detached' and volume.linode_id is not None:
            result['linode_id'] = None
            result['linode_label'] = None
            updated = True
            if not check_mode:
                volume.detach()

        if args['state'] == 'attached' and volume.linode_id is None:
            instance = _ensure_attached_instance(client, args)
            result['linode_id'] = instance.id
            result['linode_label'] = instance.label
            updated = True
            if not check_mode:
                volume.attach(instance)

        if args['state'] == 'attached' and volume.linode_id is not None:
            instance = _ensure_attached_instance(client, args)
            if volume.linode_id != instance.id:
                result['linode_id'] = instance.id
                result['linode_label'] = instance.label
                updated = True
                if not check_mode:
                    volume.detach()
                    volume.attach(instance)

        if 'size' in args:
            cur = volume.size
            if cur < args['size']:
                updated = True
                result['size'] = args['size']
                if not check_mode:
                    volume.resize(args['size'])

        return (updated, result)

    except Exception as e:
        linode_raise_client_error(e)


def volume_remove(client, volume, force=False, check_mode=False):
    try:
        if volume.linode_id is not None and not force:
            raise AnsibleError('%s volume attached' % volume.label)

        if not check_mode:
            if volume.linode_id is not None and force:
                volume.detach()
            volume.delete()

        return {'status': 'deleted'}
    except Exception as e:
        linode_raise_client_error(e)


def _fake_volume(args):
    return {
        'created': datetime.now().isoformat(),
        "filesystem_path": "/dev/disk/by-id/scsi-0Linode_Volume_my-volume-1",
        "id": -1,
        "linode_id": None,
        "linode_label": args['instance'] if 'instance' in args else None,
        "label": args['label'],
        "size": args['size'] if 'size' in args else 20,
        "region": args['region'],
        "status": "creating",
        "tags": [
            "linodes",
            "db-servers"
        ],
        'updated': datetime.now().isoformat(),
    }
