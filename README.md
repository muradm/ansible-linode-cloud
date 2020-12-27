# Ansible collection with tools to manage Linode Cloud.

Currently provides the following actions
---------------

- `instance` - manages Linode instance
- `volume` - manages Linode volume
- `domain` - manages Linode domains
- `domain_record` - manages Linode domain records

Currently provides the following roles:
--------------

- [`instance`](roles/instance/README.md) - augments inventory with Linode instances

Documentation
---------------
Extensive documentation available through `ansible-doc`. Once collection
is installed documentation is accessible with:
```
ansible-doc -t module <module>
```
For example:
```
ansible-doc -t module muradm.linode.instance
```
