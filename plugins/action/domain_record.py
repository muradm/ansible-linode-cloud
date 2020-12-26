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

        if task_vars is None:
            task_vars = {}

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        task_args = self._task.args

        check_mode = self._play_context.check_mode

        client = linode_client(task_args, task_vars)
        schema = linode_schema()

        configured = linode_action_input_validated(
            schema, 'domain_record_key', task_args)

        domain = domain_find(client, configured['domain'])
        if domain is None:
            raise AnsibleError(u'%s domain not found for record %s:%s' % (
                configured['domain'], configured['type'], configured['name']))

        domain_record = domain_record_find(
            client, domain, configured['type'], configured['name'], configured['target'])

        result = {'changed': False}

        if domain_record is None and configured['state'] == 'present':
            configured = linode_action_input_validated(
                schema, 'domain_record_create', task_args)

            result['domain_record'] = domain_record_create(
                client, domain, configured, check_mode)
            result['changed'] = True

        elif domain_record is not None and configured['state'] == 'present':
            configured = linode_action_input_validated(
                schema, 'domain_update', task_args)

            upd, res = domain_record_update(
                client, domain_record, configured, check_mode)
            result['domain_record'] = res
            result['changed'] = upd

        elif domain_record is not None and configured['state'] == 'absent':

            result['domain_record'] = domain_record_remove(
                client, domain_record, check_mode)
            result['changed'] = True

        return result
