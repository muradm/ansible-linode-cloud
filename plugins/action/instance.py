# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ..module_utils.linode.__init__ import linode_client, linode_schema, linode_action_input_validated
from ..module_utils.linode.__init__ import instance_find, instance_create, instance_update, instance_remove


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
            schema, 'instance_key', task_args)
        instance = instance_find(client, configured['label'])

        result = {'changed': False}

        if instance is None and configured['state'] == 'present':
            configured = linode_action_input_validated(
                schema, 'instance_create', task_args)

            result['instance'] = instance_create(
                client, configured, check_mode)
            result['changed'] = True

        elif instance is not None and configured['state'] == 'present':
            configured = linode_action_input_validated(
                schema, 'instance_update', task_args)

            upd, res = instance_update(
                client, instance, configured, check_mode)
            result['instance'] = res
            result['changed'] = upd

        elif instance is not None and configured['state'] == 'absent':

            result['instance'] = instance_remove(client, instance, check_mode)
            result['changed'] = True

        return result
