# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ..module_utils.linode.__init__ import linode_client, linode_schema, linode_action_input_validated
from ..module_utils.linode.__init__ import domain_find
from ..module_utils.linode.__init__ import domain_record_find, domain_record_create, domain_record_update, domain_record_remove


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        task_vars = {} if task_vars is None else task_vars
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect
        task_args = self._task.args
        check_mode = self._play_context.check_mode
        client = linode_client(task_args, task_vars)
        schema = linode_schema()

        key_args = linode_action_input_validated(
            schema, 'domain_record_key', task_args)

        domain = domain_find(client, key_args['domain'])
        if domain is None:
            raise AnsibleError(u'%s domain not found for record %s:%s' % (
                key_args['domain'], key_args['type'], key_args['name']))

        args = linode_action_input_validated(
            schema, 'domain_record', task_args)

        record = domain_record_find(domain, args)

        result = {'changed': False}

        if record is None and key_args['state'] == 'present':
            result['domain_record'] = domain_record_create(
                domain, args, check_mode)
            result['changed'] = True

        elif record is not None and key_args['state'] == 'present':
            upd, res = domain_record_update(record, args, check_mode)
            result['domain_record'] = res
            result['changed'] = upd

        elif record is not None and key_args['state'] == 'absent':
            result['domain_record'] = domain_record_remove(record, check_mode)
            result['changed'] = True

        return result
