# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ..module_utils.linode.__init__ import linode_client, linode_schema, linode_action_input_validated
from ..module_utils.linode.__init__ import domain_find, domain_create, domain_update, domain_remove


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
            schema, 'domain_key', task_args)
        domain = domain_find(client, args['domain'])

        result = {'changed': False}

        if domain is None and args['state'] == 'present':
            args = linode_action_input_validated(
                schema, 'domain_create', task_args)

            result['domain'] = domain_create(client, args, check_mode)
            result['changed'] = True

        elif domain is not None and args['state'] == 'present':
            args = linode_action_input_validated(
                schema, 'domain_update', task_args)

            upd, res = domain_update(domain, args, check_mode)
            result['domain'] = res
            result['changed'] = upd

        elif domain is not None and args['state'] == 'absent':

            result['domain'] = domain_remove(domain, check_mode)
            result['changed'] = True

        return result
