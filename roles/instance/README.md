linode.cloud.instance
=========

Reflects inventory host to linode cloud and vice versa. Instance for inventory host missing in
the cloud will be created and 'hostvars' will be populated with:

- `ansible_host` - first ipv4 address
- `ansible_user` - constant root

It should be noted that, ansible will automatically gather facts of hosts specified in playbook. To
avoid this one could use 'gather_facts: no' while applying this role. Otherwise, instance
accessible IP address for 'ansible_host' should be provided manually in the local inventory,
thus duplicated.

Role Variables
--------------

Role will expect same variables as for `linode.cloud.instance` action, but prefixed with 'linode_' in
order to avoid naming conflicts. For the list of variables refer to `linode.cloud.instance`
documentation and check example below. Role specific variables are:

- `linode_wait_for_running` - will wait for new linode instance to become booted (default `True`)
- `linode_ssh_keyscan` - will use `ssh-keyscan` and `known_hosts` task to update known hosts (default `False`)

Example Playbook
----------------

Inventory:

    all:
      hosts:
        my-linode-1:
        non-linode-1:
      children:
        linode_servers:
          hosts:
            my-linode-1:
              linode_type: g6-standard-4
              linode_image: linode/debian10
          vars:
            linode_region: eu-central
            linode_authorized_keys:
              - "ssh-rsa ..."

Playbook:

    - hosts: linode_servers
      gather_facts: no
      roles:
         - { role: linode.cloud.instance, vars: { wait_for_running: True, ssh_keyscan: True } }

License
-------

Apache-2.0

Author Information
------------------

muradm (@muradm)
