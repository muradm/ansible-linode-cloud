# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from copy import deepcopy
from datetime import datetime
from ..module_utils.linode import LinodeClientModule, _label, _original, _validate_label_match_or_empty, _is_present, _is_same_value


class ActionModule(LinodeClientModule):
    def run_linode_action(self, task_vars, result):

        label = _label('instance', self._task.args)
        is_present = _is_present('instance', self._task.args)
        original_instance = _original('ansible_linode_instance', task_vars)

        _validate_label_match_or_empty('instance', label, original_instance)

        if original_instance is None:
            original_instance = self.instance_find(label)

        if original_instance is None and is_present:
            configured = _configured_instance(self._task.args)

            if not self._play_context.check_mode:
                created = self.instance_create(configured)
            else:
                created = _fake_instance(configured)

            result = {'changed': True, 'instance': created['instance']}

            if 'root_pass' in created:
                result['root_pass'] = created['root_pass']

        elif original_instance is not None and is_present:
            configured = _configured_instance(self._task.args)

            source = deepcopy(original_instance)
            needsUpdate = False
            needsRdns = False

            if not _is_same_value(source.get('group', None), configured.get('group', None)):
                source['updated'] = datetime.now().isoformat()
                source['group'] = configured['group']
                needsUpdate = True

            if sorted(source.get('tags', [])) != sorted(configured.get('tags', [])):
                source['updated'] = datetime.now().isoformat()
                source['tags'] = configured.get('tags', [])
                needsUpdate = True

            if needsUpdate and not self._play_context.check_mode:
                to_update = self.instance_for_update(source['id'])
                if 'group' in source:
                    to_update.group = source['group']
                if 'tags' in source:
                    to_update.tags = source['tags']
                to_update.save()

            if 'ipv4_public_rdns' in configured:
                cur = self.instance_ipv4_public_rdns(source['id'])
                if cur != configured['ipv4_public_rdns']:
                    needsRdns = True
                    if not self._play_context.check_mode:
                        self.instance_set_ipv4_public_rdns(
                            source['id'], configured['ipv4_public_rdns'])

            result = {'changed': needsUpdate or needsRdns, 'instance': source}

        elif original_instance is not None and not is_present:
            if not self._play_context.check_mode:
                self.instance_for_update(original_instance['id']).delete()

            result = {'changed': True, 'instance': {'status': 'deleted'}}

        return result


def _configured_instance(task_args={}):
    args = {}

    if 'label' in task_args:
        args['label'] = task_args['label']

        if 'region' not in task_args:
            raise AnsibleError(u'%s instance missing region' % args['label'])

        args['region'] = task_args['region']

        if 'type' not in task_args:
            raise AnsibleError(u'%s instance missing type' % args['label'])

        args['type'] = task_args['type']

        if 'image' not in task_args:
            raise AnsibleError(u'%s instance missing image' % args['label'])

        args['image'] = task_args['image']

        args['tags'] = task_args.get('tags', [])

        args['authorized_keys'] = task_args.get('authorized_keys', [])

        if 'ipv4_public_rdns' in task_args:
            args['ipv4_public_rdns'] = task_args['ipv4_public_rdns']

        if 'group' in task_args:
            args['group'] = task_args['group']

        if 'root_pass' in task_args:
            args['root_pass'] = task_args['root_pass']

    else:
        raise AnsibleError(u'could not determine instance configuration')

    return args


def _fake_instance(configured):
    fake = {
        'instance': {
            'alerts': {},
            'backups': {},
            'created': datetime.now().isoformat(),
            'hypervisor': 'kvm',
            'id': -1,
            'ipv4': ["0.0.0.0"],
            'ipv6': '0000:0000::0000:0000:0000:0000/64',
            'root_pass': '1234' if 'root_pass' not in configured else configured['root_pass'],
            'specs': {},
            'status': 'booting',
            'updated': datetime.now().isoformat(),
            'watchdog_enabled': True,
            'region': configured['region'],
            'ltype': configured['type'],
            'image': configured['image'],
            'label': configured['label'],
            'group': '' if 'group' not in configured else configured['group'],
            'tags': [] if 'tags' not in configured else configured['tags'],
            'authorized_keys': configured['authorized_keys'],
        }
    }

    if 'root_pass' not in configured:
        fake['root_pass'] = 'check_mode'

    return fake
