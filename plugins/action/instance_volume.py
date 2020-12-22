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
        result = {}

        if 'instance' not in self._task.args:
            raise AnsibleError('instance not provided')

        if 'volume' not in self._task.args:
            raise AnsibleError('volume not provided')

        instance = self.instance_find(self._task.args['instance'])
        if instance is None:
            raise AnsibleError('instance %s not found' %
                               self._task.args['instance'])

        volume = self.volume_find(self._task.args['volume'])
        if volume is None:
            raise AnsibleError('volume %s not found' %
                               self._task.args['volume'])

        def present():
            if instance['id'] == volume['linode_id']:
                return False

            if self._play_context.check_mode:
                return True

            self.instance_volume_attach(instance['id'], volume['id'])
            return True

        def absent():
            if instance['id'] != volume['linode_id']:
                return False

            if self._play_context.check_mode:
                return True

            self.instance_volume_detach(instance['id'], volume['id'])
            return True

        actions = {True: present, False: absent}

        result = {
            'changed': actions[_is_present('instance_volume', self._task.args)](),
        }

        return result
