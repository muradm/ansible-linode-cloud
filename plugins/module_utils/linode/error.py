# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native

def linode_raise_client_error(e):
    from linode_api4 import ApiError, UnexpectedResponseError

    try:
        raise e
    except AnsibleError as e:
        raise e
    except ApiError as e:
        raise AnsibleError(to_native(','.join(e.errors)))
    except UnexpectedResponseError as e:
        raise AnsibleError(u'unexpected client error: %s' % to_native(e))
