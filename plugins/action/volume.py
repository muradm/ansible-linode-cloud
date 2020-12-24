# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from copy import deepcopy
from datetime import datetime
from ..module_utils.linode import LinodeClientModule, _label, _is_present, _is_same_value


class ActionModule(LinodeClientModule):
    def run_linode_action(self, task_vars, result):
        label = _label('volume', self._task.args)
        is_present = _is_present('volume', self._task.args)
        original_volume = self.volume_find(label)

        if original_volume is None and is_present:
            configured = _configured_volume(self._task.args)

            if not self._play_context.check_mode:
                created = self.volume_create(configured)
            else:
                created = _fake_volume(configured)

            result = {'changed': True, 'volume': created['volume']}

        elif original_volume is not None and is_present:
            configured = _configured_volume(self._task.args)

            source = deepcopy(original_volume)
            needsUpdate = False
            needsResize = False

            if sorted(source.get('tags', [])) != sorted(configured.get('tags', [])):
                source['updated'] = datetime.now().isoformat()
                source['tags'] = configured.get('tags', [])
                needsUpdate = True

            if not _is_same_value(source.get('size', None), configured.get('size', None)):
                source['updated'] = datetime.now().isoformat()
                source['size'] = configured['size']
                needsResize = True

            if needsUpdate and not self._play_context.check_mode:
                to_update = self.volume_for_update(source['id'])
                if 'tags' in source:
                    to_update.tags = source['tags']
                to_update.save()

            if needsResize and not self._play_context.check_mode:
                to_update = self.volume_for_update(source['id'])
                to_update.resize(source['size'])

            result = {
                'changed': needsUpdate or needsResize,
                'volume': source,
            }

        elif original_volume is not None and not is_present:
            if not self._play_context.check_mode:
                self.volume_for_update(original_volume['id']).delete()

            result = {'changed': True, 'volume': {'status': 'deleted'}}

        return result


def _configured_volume(task_args={}):
    args = {}

    if 'label' in task_args:
        args['label'] = task_args['label']

        if 'region' not in task_args:
            raise AnsibleError(u'%s volume missing region' % args['label'])

        args['region'] = task_args['region']

        if 'size' not in task_args:
            raise AnsibleError(u'%s volume missing size' % args['label'])

        args['size'] = task_args['size']

        args['tags'] = task_args.get('tags', [])

    else:
        raise AnsibleError(u'could not determine instance configuration')

    return args


def _fake_volume(configured):
    return {
        'volume': {
            'created': datetime.now().isoformat(),
            'filesystem_path': '/dev/disk/by-id/%s' % configured['label'],
            'id': -1,
            'linode_id': None,
            'linode_label': None,
            'status': 'creating',
            'updated': datetime.now().isoformat(),
            'region': configured['region'],
            'size': configured['size'],
            'label': configured['label'],
            'tags': [] if 'tags' not in configured else configured['tags'],
        }
    }
