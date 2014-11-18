from __future__ import absolute_import
from ...base import Context, ContainerType
from .objects import (
    Schema,
    Swagger,
    Info,
    Items,
    Parameter,
    Header,
    Response,
    Operation,
    PathItem,
    SecurityScheme,
    Tag
)


class ItemsContext(Context):
    """ Context of Item Object
    """

    __swagger_ref_object__ = Items

# self-reference 
setattr(ItemsContext, '__swagger_child__', [
    ('items', None, ItemsContext),
])


class SchemaContext(Context):
    """ Context of Schema Object
    """

    __swagger_ref_object__ = Schema

# self-reference 
setattr(SchemaContext, '__swagger_child__', [
    # items here should refer to an Schema Object.
    # refer to https://github.com/swagger-api/swagger-spec/issues/165
    # for details
    ('items', None, SchemaContext),
    ('properties', ContainerType.dict_, SchemaContext),
    ('allOf', ContainerType.list_, SchemaContext),
])



class ParameterContext(Context):
    """ Context of Parameter Object, along with
    Reference Object
    """

    __swagger_child__ = [
        ('schema', None, SchemaContext),
        # items here should refer to an Items Object.
        # refer to https://github.com/swagger-api/swagger-spec/issues/165
        # for details
        ('items', None, ItemsContext),
    ]
    __swagger_ref_object__ = Parameter


class HeaderContext(Context):
    """ Context of Header Object
    """

    __swagger_child__ = [
        ('items', None, ItemsContext),
    ]
    __swagger_ref_object__ = Header


class ResponseContext(Context):
    """ Context of Response Object
    """

    __swagger_child__ = [
        ('schema', None, SchemaContext),
        ('headers', ContainerType.dict_, HeaderContext),
    ]
    __swagger_ref_object__ = Response


class OperationContext(Context):
    """ Context of Operation Object
    """

    __swagger_child__ = [
        ('parameters', ContainerType.list_, ParameterContext),
        ('responses', ContainerType.dict_, ResponseContext),
    ]
    __swagger_ref_object__ = Operation


class PathItemContext(Context):
    """ Context of Path Item Object
    """

    __swagger_child__ = [
        ('get', None, OperationContext),
        ('put', None, OperationContext),
        ('post', None, OperationContext),
        ('delete', None, OperationContext),
        ('options', None, OperationContext),
        ('head', None, OperationContext),
        ('patch', None, OperationContext),
        ('parameters', ContainerType.list_, ParameterContext),
    ]
    __swagger_ref_object__ = PathItem


class SecuritySchemeContext(Context):
    """ Context of Security Schema Object
    """

    __swagger_ref_object__ = SecurityScheme


class TagContext(Context):
    """ Context of Tag Object
    """

    __swagger_ref_object__ = Tag


class InfoContext(Context):
    """ Context of Info Object
    """

    __swagger_ref_object__ = Info


class SwaggerContext(Context):
    """ Context of Swagger Object
    """

    __swagger_child__ = [
        ('info', None, InfoContext),
        ('paths', ContainerType.dict_, PathItemContext),
        ('definitions', ContainerType.dict_, SchemaContext),
        ('parameters', ContainerType.dict_, ParameterContext),
        ('responses', ContainerType.dict_, ResponseContext),
        ('securityDefinitions', ContainerType.dict_, SecuritySchemeContext),
        ('tags', ContainerType.list_, TagContext),
    ]
    __swagger_ref_object__ = Swagger
