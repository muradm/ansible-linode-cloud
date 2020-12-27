# Ansible collection with tools to manage Linode Cloud.

Currently provides the following actions
---------------

- `instance` - manages Linode instance
- `volume` - manages Linode volume
- `domain` - manages Linode domains
- `domain_record` - manages Linode domain records
- `balancer` - manager Linode balancer
- `balancer_config` - manages Linode balancer config
- `balancer_node` - manages Linode balancer config node

Currently provides the following roles:
--------------

- [`instance`](roles/instance/README.md) - augments inventory with Linode instances

Dependencies
---------------

Before using this collection, make sure that the following Python libraries are in path.

- [`linode_api4`](https://pypi.org/project/linode-api4/) - The official python library for the Linode API v4 in python
- [`netaddr`](https://pypi.org/project/netaddr/) - A system-independent network address manipulation library preferred by Ansible for filters
- [`cerberus`](https://pypi.org/project/cerberus/) - Cerberus is a lightweight and extensible data validation library for Python used to validate action inputs

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
