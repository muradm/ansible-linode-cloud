# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ..module_utils.linode.__init__ import linode_client, linode_schema, linode_action_input_validated
from ..module_utils.linode.__init__ import balancer_find, balancer_create, balancer_update, balancer_remove


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
            schema, 'balancer_key', task_args)
        balancer = balancer_find(client, configured['label'])

        result = {'changed': False}

        if balancer is None and configured['state'] == 'present':
            configured = linode_action_input_validated(
                schema, 'balancer_create', task_args)

            result['balancer'] = balancer_create(client, configured, check_mode)
            result['changed'] = True

        elif balancer is not None and configured['state'] == 'present':
            configured = linode_action_input_validated(
                schema, 'balancer_update', task_args)

            upd, res = balancer_update(client, balancer, configured, check_mode)
            result['balancer'] = res
            result['changed'] = upd

        elif balancer is not None and configured['state'] == 'absent':

            result['balancer'] = balancer_remove(client, balancer, check_mode)
            result['changed'] = True

        return result
