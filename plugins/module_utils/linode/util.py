
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, muradm <mail@muradm.net>
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def _filter_dict_keys(d: dict, keys: list) -> dict:
    return {k: v for k, v in d.items() if not (k in keys) and v is not None}


def _update_if_needed(target, updated, args, field, check_mode, to_be_sorted=False, to_be_lower=False):
    if field not in args:
        return False

    if to_be_sorted:
        if sorted(getattr(target, field)) == sorted(args[field]):
            return False

    if to_be_lower:
        if field in args and str(getattr(target, field)).lower() == str(args[field]).lower():
            return False

    if getattr(target, field) == args[field]:
        return False

    if not check_mode:
        setattr(target, field, args[field])
    updated[field] = args[field]

    return True
