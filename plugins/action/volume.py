# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ..module_utils.linode.__init__ import linode_client, linode_schema, linode_action_input_validated
from ..module_utils.linode.__init__ import volume_find, volume_create, volume_update, volume_remove


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = {}

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        task_args = self._task.args

        check_mode = self._play_context.check_mode

        client = linode_client(task_args, task_vars)
        schema = linode_schema()

        configured = linode_action_input_validated(
            schema, 'volume_key', task_args)
        volume = volume_find(client, configured['label'])

        result = {'changed': False}

        if volume is None and configured['state'] in ['attached', 'detached']:
            configured = linode_action_input_validated(
                schema, 'volume_create', task_args)

            result['volume'] = volume_create(client, configured, check_mode)
            result['changed'] = True

        elif volume is not None and configured['state'] in ['attached', 'detached']:
            configured = linode_action_input_validated(
                schema, 'volume_update', task_args)

            upd, res = volume_update(client, volume, configured, check_mode)
            result['volume'] = res
            result['changed'] = upd

        elif volume is not None and configured['state'] == 'absent':
            configured = linode_action_input_validated(
                schema, 'volume_remove', task_args)

            result['volume'] = volume_remove(client, volume, check_mode)
            result['changed'] = True

        return result
