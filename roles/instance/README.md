muradm.linode.instance
=========

Reflects inventory host to linode cloud and vice versa. Instance for inventory host missing in
the cloud will be created and 'hostvars' will be populated with:

- `ansible_host` - first ipv4 address
- `ansible_user` - constant root

It should be noted that, ansible will automatically gather facts of hosts specified in playbook. To
avoid this one could use 'gather_facts: no' while applying this role. Otherwise, instance
accessible IP address for 'ansible_host' should be provided manually in the local inventory,
thus duplicated.

Requirements
--------------

- `linode_api4`
- `netaddr`

Role Variables
--------------

Role will expect same variables as for `muradm.linode.instance` action, but prefixed with 'linode_' in
order to avoid naming conflicts. For the list of variables refer to `muradm.linode.instance`
documentation and check example below. Role specific variables are:

- `linode_wait_for_running` - will wait for new linode instance to become booted (default `True`)
- `linode_ssh_keyscan` - will use `ssh-keyscan` and `known_hosts` task to update known hosts (default `False`)

Use Cases
----------------

Non-intrusive existing inventory management
^^^^^^^^^^^^^^

Suppose you have an Ansible setup already, and you want on-board some servers from Linode Cloud. Let's
assume the following inventory example:

    all:
      hosts:
        host-1:
        host-2:
        old-host-1:
        old-host-2:
        host1.mydomain.com:
        host2.mydomain.com:

      old-hosts:
        hosts:
          old-host-1:
            ansible_host: 172.17.0.10
          old-host-2:
            ansible_host: 172.17.0.11

      inhouse-hosts:
        hosts:
          host-1:
            ansible_host: 192.168.0.12
          host-2:
            ansible_host: 192.168.0.13

      some-cloud-hosts:
        hosts:
          host1.mydomain.com:
          host2.mydomain.com:


Now we want to add few servers from Linode Cloud. Changes to do in inventory:

    all:
      hosts:
        # ... unchaged
        # below added
        linode-01:
        linode-02:
      
      # ... unchanged
      some-cloud-hosts:
        hosts:
          host1.mydomain.com:
          host2.mydomain.com:
      # below added
      linodes:
        hosts:
          linode-01:
            linode_type: g6-standard-1
            linode_image: linode/debian10
          linode-02:
            linode_type: g6-standard-1
            linode_image: linode/debian10
        vars:
          linode_region: eu-central
          linode_authorized_keys:
            - "ssh-rsa AAAA ..."


Once inventory is ready, in your playbooks, somewhere at early stages:

    - hosts: linodes
      gather_facts: no
      roles:
         - { role: muradm.linode.instance, vars: { wait_for_running: True, ssh_keyscan: True } }


Gathering facts will be off for this task, since IP addresses and other information is
simply not available yet. In addition, `ssh_keyscan` will attempt to add discovered hosts
to your `~/.ssh/known_hosts` using `ssh-keyscan`.

This role will connect to Linode Cloud, lookup every host by label. If such linode instance
exists, will collect information and fill `ansible_host`, `ansible_user`, so that
subsequent tasks, can do normal job. If such linode instances do not exists, it will
automatically create them as per inventory configuration.


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
         - { role: muradm.linode.instance, vars: { wait_for_running: True, ssh_keyscan: True } }

License
-------

Apache-2.0

Author Information
------------------

muradm (@muradm)
