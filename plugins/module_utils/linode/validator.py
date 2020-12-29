# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.utils.display import Display


log = Display()


def _check_state(f, v, error):
    if v is not None:
        if v not in ['present', 'absent']:
            error(f, 'state should be present or absent, but got %s' % v)


def _check_volume_state(f, v, error):
    if v is not None:
        if v not in ['detached', 'attached', 'absent']:
            error(f, 'state should be detached, attached or absent, but got %s' % v)


DOMAIN_RECORD_TYPES = ['NS', 'MX', 'A', 'AAAA',
                       'CNAME', 'TXT', 'SRV', 'CAA', 'PTR']
DOMAIN_RECORD_TYPES_JOINED = ','.join(DOMAIN_RECORD_TYPES)


def _check_domain_record_type(f, v, error):
    if v is not None and isinstance(v, str):
        if str(v).upper() not in DOMAIN_RECORD_TYPES:
            error(f, 'domain record type should be one of %s, but got %s' %
                  (DOMAIN_RECORD_TYPES_JOINED, str(v).upper()))


DOMAIN_RECORD_SRV_PROTOCOLS = ['tcp', 'udp', 'xmpp', 'tls', 'smtp']
DOMAIN_RECORD_SRV_PROTOCOLS_JOINED = ','.join(DOMAIN_RECORD_SRV_PROTOCOLS)


def _check_domain_record_srv_protocol(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in DOMAIN_RECORD_SRV_PROTOCOLS:
            error(f, 'domain SRV record protocol should one of %s, but got %s' %
                  (DOMAIN_RECORD_SRV_PROTOCOLS_JOINED, v))


DOMAIN_RECORD_CAA_TAG = ['issue', 'issuewild', 'iodef']
DOMAIN_RECORD_CAA_TAG_JOINED = ','.join(DOMAIN_RECORD_CAA_TAG)


def _check_domain_record_caa_tag(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in DOMAIN_RECORD_CAA_TAG:
            error(f, 'domain CAA record tag should one of %s, but got %s' %
                  (DOMAIN_RECORD_CAA_TAG_JOINED, v))


DOMAIN_TYPES = ['master', 'slave']
DOMAIN_TYPES_JOINED = ','.join(DOMAIN_TYPES)


def _check_domain_type(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in DOMAIN_TYPES:
            error(f, 'domain type should one of %s, but got %s' %
                  (DOMAIN_TYPES_JOINED, v))


BALANCER_CONFIG_ALGORITHMS = ['roundrobin', 'leastconn', 'source']
BALANCER_CONFIG_ALGORITHMS_JOINED = ','.join(BALANCER_CONFIG_ALGORITHMS)


def _check_balancer_config_algorithm(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in BALANCER_CONFIG_ALGORITHMS:
            error(f, 'balancer config algorithm should one of %s, but got %s' %
                  (BALANCER_CONFIG_ALGORITHMS_JOINED, v))


BALANCER_CONFIG_CHECKS = ['none', 'connection', 'http', 'http_body']
BALANCER_CONFIG_CHECKS_JOINED = ','.join(BALANCER_CONFIG_CHECKS)


def _check_balancer_config_check(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in BALANCER_CONFIG_CHECKS:
            error(f, 'balancer config check should one of %s, but got %s' %
                  (BALANCER_CONFIG_CHECKS_JOINED, v))


BALANCER_CONFIG_CIPHER_SUITES = ['recommended', 'legacy']
BALANCER_CONFIG_CIPHER_SUITES_JOINED = ','.join(BALANCER_CONFIG_CIPHER_SUITES)


def _check_balancer_config_cipher_suite(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in BALANCER_CONFIG_CIPHER_SUITES:
            error(f, 'balancer config cipher suite should one of %s, but got %s' %
                  (BALANCER_CONFIG_CIPHER_SUITES_JOINED, v))


BALANCER_CONFIG_PROTOCOLS = ['http', 'https', 'tcp']
BALANCER_CONFIG_PROTOCOLS_JOINED = ','.join(BALANCER_CONFIG_PROTOCOLS)


def _check_balancer_config_protocol(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in BALANCER_CONFIG_PROTOCOLS:
            error(f, 'balancer config protocol should one of %s, but got %s' %
                  (BALANCER_CONFIG_PROTOCOLS_JOINED, v))


BALANCER_CONFIG_PROXY_PROTOCOLS = ['none', 'v1', 'v2']
BALANCER_CONFIG_PROXY_PROTOCOLS_JOINED = ','.join(
    BALANCER_CONFIG_PROXY_PROTOCOLS)


def _check_balancer_config_proxy_protocol(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in BALANCER_CONFIG_PROXY_PROTOCOLS:
            error(f, 'balancer config proxy protocol should one of %s, but got %s' %
                  (BALANCER_CONFIG_PROXY_PROTOCOLS_JOINED, v))


BALANCER_CONFIG_STICKINESSES = ['none', 'table', 'http_cookie']
BALANCER_CONFIG_STICKINESSES_JOINED = ','.join(BALANCER_CONFIG_STICKINESSES)


def _check_balancer_config_stickiness(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in BALANCER_CONFIG_STICKINESSES:
            error(f, 'balancer config stickiness should one of %s, but got %s' %
                  (BALANCER_CONFIG_STICKINESSES_JOINED, v))


BALANCER_NODE_MODES = ['accept', 'reject', 'drain', 'backup']
BALANCER_NODE_MODES_JOINED = ','.join(BALANCER_NODE_MODES)


def _check_balancer_node_mode(f, v, error):
    if v is not None and isinstance(v, str):
        if v.lower() not in BALANCER_NODE_MODES:
            error(f, 'balancer node mode should one of %s, but got %s' %
                  (BALANCER_NODE_MODES_JOINED, v))


LINODE_TAGS_TYPE = {'type': 'list', 'schema': {
    'type': 'string'}, 'required': False, 'default': []}


def linode_schema():
    try:
        from cerberus.schema import SchemaRegistry
    except ImportError:
        raise AnsibleError('could not import cerberus module')

    schema = SchemaRegistry()

    schema.add('instance_key', {
        'label': {'type': 'string', 'required': True},
        'state': {'check_with': _check_state, 'required': False, 'default': 'present'},
    })

    schema.add('instance_create', {
        'label': {'type': 'string', 'required': True},
        'region': {'type': 'string', 'required': True},
        'type': {'type': 'string', 'required': True},
        'image': {'type': 'string', 'required': True},
        'group': {'type': 'string', 'required': False},
        'root_pass': {'type': 'string', 'required': False},
        'tags': LINODE_TAGS_TYPE,
        'authorized_keys': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []},
        'ipv4_public_rdns': {'type': 'string', 'required': False},
        'private_ip': {'type': 'boolean', 'required': False, 'default': False},
    })

    schema.add('instance_update', {
        'label': {'type': 'string', 'required': True},
        'type': {'type': 'string', 'required': False},
        'image': {'type': 'string', 'required': False},
        'group': {'type': 'string', 'required': False},
        'tags': LINODE_TAGS_TYPE,
        'ipv4_public_rdns': {'type': 'string', 'required': False},
        'private_ip': {'type': 'boolean', 'required': False},
    })

    schema.add('volume_key', {
        'label': {'type': 'string', 'required': True},
        'state': {'check_with': _check_volume_state, 'required': False, 'default': 'detached'},
    })

    schema.add('volume_create', {
        'label': {'type': 'string', 'required': True},
        'region': {'type': 'string', 'required': False},
        'size': {'type': 'integer', 'required': False, 'default': 20},
        'tags': LINODE_TAGS_TYPE,
        'instance': {'type': 'string', 'required': False},
        'state': {'check_with': _check_volume_state, 'required': False, 'default': 'detached'},
    })

    schema.add('volume_update', {
        'label': {'type': 'string', 'required': True},
        'size': {'type': 'integer', 'required': False},
        'tags': LINODE_TAGS_TYPE,
        'instance': {'type': 'string', 'required': False},
        'state': {'check_with': _check_volume_state, 'required': False, 'default': 'detached'},
    })

    schema.add('volume_remove', {
        'label': {'type': 'string', 'required': True},
        'force': {'type': 'boolean', 'required': False, 'default': False},
    })

    schema.add('domain_record', {
        'type': {'check_with': _check_domain_record_type, 'required': True},
        'name': {'type': 'string', 'required': True},
        'target': {'type': 'string', 'required': True},
        'ttl_sec': {'type': 'integer', 'required': False},
        'protocol': {'check_with': _check_domain_record_srv_protocol},
        'priority': {'type': 'integer', 'required': False},
        'weight': {'type': 'integer', 'required': False},
        'port': {'type': 'integer', 'required': False},
        'service': {'type': 'string', 'required': False},
        'tag': {'check_with': _check_domain_record_caa_tag},
    })

    schema.add('domain_key', {
        'domain': {'type': 'string', 'required': True},
        'state': {'check_with': _check_state, 'required': False, 'default': 'present'},
    })

    schema.add('domain_create', {
        'domain': {'type': 'string', 'required': True},
        'soa_email': {'type': 'string', 'required': False},
        'type': {'check_with': _check_domain_type, 'required': True},
        'group': {'type': 'string', 'required': False},
        'description': {'type': 'string', 'required': False},
        'retry_sec': {'type': 'integer', 'required': False},
        'expire_sec': {'type': 'integer', 'required': False},
        'refresh_sec': {'type': 'integer', 'required': False},
        'ttl_sec': {'type': 'integer', 'required': False},
        'master_ips': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []},
        'axfr_ips': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []},
        'tags': LINODE_TAGS_TYPE,
        'records': {'type': 'list', 'schema': {'schema': schema.get('domain_record')}},
    })

    schema.add('domain_update', {
        'domain': {'type': 'string', 'required': True},
        'soa_email': {'type': 'string', 'required': False},
        'group': {'type': 'string', 'required': False},
        'description': {'type': 'string', 'required': False},
        'retry_sec': {'type': 'integer', 'required': False},
        'expire_sec': {'type': 'integer', 'required': False},
        'refresh_sec': {'type': 'integer', 'required': False},
        'ttl_sec': {'type': 'integer', 'required': False},
        'master_ips': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []},
        'axfr_ips': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []},
        'tags': LINODE_TAGS_TYPE,
        'records': {'type': 'list', 'schema': {'schema': schema.get('domain_record')}},
        'keep_unknown_records': {'type': 'boolean', 'required': False, 'default': True},
        'return_unknown_records': {'type': 'boolean', 'required': False, 'default': False},
    })

    schema.add('balancer_node_key', {
        'balancer': {'type': 'string', 'required': True},
        'port': {'type': 'integer', 'min': 1, 'max': 65535, 'required': True},
        'address': {'type': 'string', 'required': True},
        'state': {'check_with': _check_state, 'required': False, 'default': 'present'},
    })

    schema.add('balancer_node_create', {
        'address': {'type': 'string', 'required': True},
        'label': {'type': 'string', 'required': True},
        'mode': {'check_with': _check_balancer_node_mode, 'required': False, 'default': 'accept'},
        'weight': {'type': 'integer', 'min': 1, 'max': 255, 'required': False, 'default': 1},
    })

    schema.add('balancer_node_update', {
        'mode': {'check_with': _check_balancer_node_mode, 'required': False, 'default': 'accept'},
        'weight': {'type': 'integer', 'min': 1, 'max': 255, 'required': False, 'default': 0},
    })

    schema.add('balancer_config_key', {
        'balancer': {'type': 'string', 'required': True},
        'port': {'type': 'integer', 'min': 1, 'max': 65535, 'required': True},
        'state': {'check_with': _check_state, 'required': False, 'default': 'present'},
    })

    schema.add('balancer_config_create', {
        'port': {'type': 'integer', 'min': 1, 'max': 65535, 'required': True},
        'protocol': {'check_with': _check_balancer_config_protocol, 'required': True},
        'algorithm': {'check_with': _check_balancer_config_algorithm, 'required': True},
        'stickiness': {'check_with': _check_balancer_config_stickiness, 'required': True},

        # when protocol 'tcp'
        'proxy_protocol': {'check_with': _check_balancer_config_proxy_protocol, 'required': False, 'default': 'none'},

        # when protocol 'https'
        'ssl_cert': {'type': 'string', 'required': False},
        'ssl_key': {'type': 'string', 'required': False},
        'cipher_suite': {'check_with': _check_balancer_config_cipher_suite, 'required': False, 'default': 'recommended'},

        'check': {'check_with': _check_balancer_config_check, 'required': False, 'default': 'none'},

        # common to all checks
        'check_passive': {'type': 'boolean', 'required': False},
        'check_interval': {'type': 'integer', 'required': False},
        'check_timeout': {'type': 'integer', 'min': 1, 'max': 30, 'required': False},
        'check_attempts': {'type': 'integer', 'min': 1, 'max': 30, 'required': False},

        # when check 'http'
        'check_path': {'type': 'string', 'required': False},
        # when check 'http_body'
        'check_body': {'type': 'string', 'required': False},

        'nodes': {'type': 'list', 'schema': {'schema': schema.get('balancer_node_create')}, 'required': False, 'default': []},

        'keep_unknown_nodes': {'type': 'boolean', 'required': False, 'default': True},
        'return_unknown_nodes': {'type': 'boolean', 'required': False, 'default': False},
    })

    schema.add('balancer_config_update', schema.get('balancer_config_create'))

    schema.add('balancer_key', {
        'label': {'type': 'string', 'required': True},
        'state': {'check_with': _check_state, 'required': False, 'default': 'present'},
    })

    schema.add('balancer_create', {
        'label': {'type': 'string', 'minlength': 3, 'maxlength': 32, 'required': True},
        'region': {'type': 'string', 'required': True},
        'client_conn_throttle': {'type': 'integer', 'min': 0, 'max': 20, 'required': False, 'default': 0},

        # AttributeError: 'NodeBalancer' object has no attribute 'tags'
        # 'tags': LINODE_TAGS_TYPE,

        'configs': {'type': 'list', 'schema': {'schema': schema.get('balancer_config_create')}, 'required': False, 'default': []},

        'keep_unknown_configs': {'type': 'boolean', 'required': False, 'default': True},
        'return_unknown_configs': {'type': 'boolean', 'required': False, 'default': False},

        'ipv4_public_rdns': {'type': 'string', 'required': False},
    })

    schema.add('balancer_update', {
        'client_conn_throttle': {'type': 'integer', 'min': 0, 'max': 20, 'required': False},

        # AttributeError: 'NodeBalancer' object has no attribute 'tags'
        # 'tags': LINODE_TAGS_TYPE,

        'configs': {'type': 'list', 'schema': {'schema': schema.get('balancer_config_create')}, 'required': False, 'default': []},

        'keep_unknown_configs': {'type': 'boolean', 'required': False, 'default': True},
        'return_unknown_configs': {'type': 'boolean', 'required': False, 'default': False},

        'ipv4_public_rdns': {'type': 'string', 'required': False},
    })

    return schema


def linode_action_input_validated(schema, definition, args):
    from cerberus import Validator
    from pprint import pformat
    from json import dumps

    log.vvvvv('linode_action_input_validated(%s): %s' %
              (definition, str(args)))

    v = Validator(
        schema=schema.get(definition),
        purge_unknown=True,
    )

    normalized = v.normalized(args)

    log.vvvvv('linode_action_input_validated(%s): normalized %s' %
              (definition, str(normalized)))

    if not v.validate(normalized):
        for err in dumps(v.errors, indent=2).split("\n"):
            log.warning('linode_action_input_validated(%s): %s' %
                        (definition, err))
        raise AnsibleError('while validating %s got errors: %s' %
                           (definition, str(v.errors)))

    validated = v.validated(args)

    log.vvv('linode_action_input_validated(%s): validated %s' %
            (definition, str(validated)))

    return validated
