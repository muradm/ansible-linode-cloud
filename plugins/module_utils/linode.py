from abc import abstractmethod
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.module_utils.ansible_release import __version__ as ansible_version
from ansible.plugins.action import ActionBase
from copy import deepcopy
from os import environ



class LinodeClientModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}

        result = super(LinodeClientModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        try:
            from linode_api4 import LinodeClient
        except ImportError:
            raise AnsibleError('could not import linode_api4 module')

        at = self._task.args.get(
            'access_token',
            task_vars.get(
                'linode_access_token',
                environ.get('LINODE_ACCESS_TOKEN', None)
            )
        )

        if at is None:
            raise AnsibleError('could not resolve linode access token')

        user_agent = 'Ansible-linode_api4/%s' % ansible_version

        self._client = LinodeClient(at, user_agent=user_agent)

        return self.run_linode_action(task_vars, result)

    @abstractmethod
    def run_linode_action(self, client, result, task_vars=None):
        pass

    def raise_client_error(self, e):
        from linode_api4 import ApiError, UnexpectedResponseError

        try:
            raise e
        except ApiError as e:
            raise AnsibleError(to_native(','.join(e.errors)))
        except UnexpectedResponseError as e:
            raise AnsibleError(u'unexpected client error: %s' % to_native(e))

    def instance_find(self, label):
        from linode_api4 import Instance

        try:
            return deepcopy(self._client.linode.instances(Instance.label == label)[0]._raw_json)
        except IndexError:
            return None
        except Exception as e:
            self.raise_client_error(e)

    def instance_create(self, args):
        non_optional = ['region', 'type', 'image', 'label', 'authorized_keys']

        remaining = {k: v for k, v in args.items() if not (
            k in non_optional) and v is not None}

        try:
            response = self._client.linode.instance_create(
                ltype=args['type'],
                region=args['region'],
                image=args['image'],
                authorized_keys=args['authorized_keys'],
                label=args['label'],
                **remaining
            )

            result = {}

            if isinstance(response, tuple):
                instance, root_pass = response
                result['instance'] = deepcopy(instance._raw_json)
                result['root_pass'] = root_pass
            else:
                instance = response
                result['instance'] = deepcopy(instance._raw_json)

            if 'ipv4_public_rdns' in args:
                instance.ips.ipv4.public.rdns = args['ipv4_public_rdns']

            if 'ipv4_private_ip' in args:
                self.instance_allocate_ipv4_private_ip(instance, public=False)

        except Exception as e:
            self.raise_client_error(e)

        return result

    def instance_for_update(self, id):
        from linode_api4 import Instance

        try:
            return self._client.load(Instance, id)
        except Exception as e:
            self.raise_client_error(e)

    def instance_ipv4_public_rdns(self, id):
        from linode_api4 import Instance

        try:
            return self._client.load(Instance, id).ips.ipv4.public[0].rdns
        except Exception as e:
            self.raise_client_error(e)

    def instance_set_ipv4_public_rdns(self, id, ipv4_public_rdns):
        from linode_api4 import Instance

        try:
            instance = self._client.load(Instance, id)
            instance.ips.ipv4.public[0].rdns = ipv4_public_rdns
            instance.ips.ipv4.public[0].save()
            return True
        except Exception as e:
            self.raise_client_error(e)

    def instance_ipv4_private_ip(self, id):
        from linode_api4 import Instance

        try:
            return self._client.load(Instance, id).ips.ipv4.private[0]
        except IndexError:
            return None
        except Exception as e:
            self.raise_client_error(e)

    def instance_allocate_ipv4_private_ip(self, id):
        try:
            return self._client.networking.ip_allocate(id, public=False)
        except Exception as e:
            self.raise_client_error(e)

    def volume_find(self, label):
        from linode_api4 import Volume

        try:
            return deepcopy(self._client.volumes(Volume.label == label)[0]._raw_json)
        except IndexError:
            return None
        except Exception as e:
            self.raise_client_error(e)

    def volume_create(self, args):
        non_optional = ['region', 'size', 'label', 'linode']

        remaining = {k: v for k, v in args.items() if not (
            k in non_optional) and v is not None}

        try:
            response = self._client.volume_create(
                region=args['region'],
                label=args['label'],
                size=args['size'],
                **remaining
            )

            result = {'volume': deepcopy(response._raw_json)}

        except Exception as e:
            self.raise_client_error(e)

        return result

    def volume_for_update(self, id):
        from linode_api4 import Volume

        try:
            return self._client.load(Volume, id)
        except Exception as e:
            self.raise_client_error(e)

    def instance_volume_attach(self, instance_id, volume_id):
        from linode_api4 import Volume

        try:
            return self._client.load(Volume, volume_id).attach(instance_id)
        except Exception as e:
            self.raise_client_error(e)

    def instance_volume_detach(self, instance_id, volume_id):
        from linode_api4 import Volume

        try:
            return self._client.load(Volume, volume_id).detach()
        except Exception as e:
            self.raise_client_error(e)


def _label(otype, task_args={}):
    if 'label' not in task_args:
        raise AnsibleError(u'%s label not set' % otype)
    return task_args['label']


def _is_present(otype, task_args={}):
    state = task_args.get('state')

    if state and state == 'present':
        return True
    elif state and state == 'absent':
        return False
    elif state is None:
        return True
    else:
        raise AnsibleError(u'unexpected %s state' % otype)


def _validate_label_match_or_empty(otype, label, obj):
    if obj is None:
        return

    if 'label' not in obj or obj['label'] != label:
        raise AnsibleError(
            u'argument label %s is not %s label' % (label, otype))


def _original(key, task_vars={}):
    return task_vars.get(key, None)


def _is_same_value(a, b):
    return (not a and not b) or (a == b)
