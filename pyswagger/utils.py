from __future__ import absolute_import
from .const import SCOPE_SEPARATOR


def compose_scope(scope, name):
    new_scope = scope if scope else name
    if scope and name:
        new_scope = scope + SCOPE_SEPARATOR + name

    return new_scope
 
