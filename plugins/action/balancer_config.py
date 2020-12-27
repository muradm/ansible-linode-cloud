# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ..module_utils.linode.__init__ import linode_client, linode_schema, linode_action_input_validated
from ..module_utils.linode.__init__ import balancer_find
from ..module_utils.linode.__init__ import balancer_config_find, balancer_config_create, balancer_config_update, balancer_config_remove


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        task_vars = {} if task_vars is None else task_vars
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect
        task_args = self._task.args
        check_mode = self._play_context.check_mode
        client = linode_client(task_args, task_vars)
        schema = linode_schema()

        args = linode_action_input_validated(
            schema, 'balancer_config_key', task_args)

        balancer = balancer_find(client, args['balancer'])
        if balancer is None:
            raise AnsibleError('%s balancer not found for config %s' % (
                args['balancer'], args['port']))

        config = balancer_config_find(balancer, args['port'])

        result = {'changed': False}

        if config is None and args['state'] == 'present':
            args = linode_action_input_validated(
                schema, 'balancer_config_create', task_args)

            result['balancer_config'] = balancer_config_create(
                balancer, args, check_mode)
            result['changed'] = True

        elif config is not None and args['state'] == 'present':
            args = linode_action_input_validated(
                schema, 'balancer_config_update', task_args)

            upd, res = balancer_config_update(config, args, check_mode)
            result['balancer_config'] = res
            result['changed'] = upd

        elif config is not None and args['state'] == 'absent':
            result['balancer_config'] = balancer_config_remove(
                config, check_mode)
            result['changed'] = True

        return result
