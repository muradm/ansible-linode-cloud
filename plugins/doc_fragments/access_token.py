# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
    options:
      access_token:
        description:
          Linode API access token to use for authentication. Can be provided as following:
              - on every action arguments
              - in hostvars as `linode_access_token`
              - in environment as `LINODE_ACCESS_TOKEN`
        type: str
        required: true
    '''
