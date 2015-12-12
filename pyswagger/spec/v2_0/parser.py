from __future__ import absolute_import
from ..base import (
    Context,
    ContainerType,
    BaseObj,
    NullContext
    )
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
    Tag,
    ExternalDocumentation,
    Contact,
    License,
    XMLObject)


class ExternalDocumentationContext(Context):
    """ Context of External Document
    """

    __swagger_ref_object__ = ExternalDocumentation


class XMLObjectContext(Context):
    """ Context of XML Object
    """

    __swagger_ref_object__ = XMLObject


class ItemsContext(Context):
    """ Context of Item Object
    """

    __swagger_ref_object__ = Items

# self-reference 
setattr(ItemsContext, '__swagger_child__', {
    'items': (None, ItemsContext),
})


class SchemaContext(Context):
    """ Context of Schema Object
    """

    __swagger_ref_object__ = Schema
    __swagger_child__ = {
        'xml': (None, XMLObjectContext),
        'externalDocs': (None, ExternalDocumentationContext),
    }


class AdditionalPropertiesContext(Context):
    """ Context of additionalProperties,
    """

    class _TmpObj(BaseObj):
        def merge(self, other, _):
            if isinstance(other, bool):
                return other

            ret = Schema(NullContext())
            return ret.merge(other, SchemaContext)

    @classmethod
    def is_produced(kls, obj):
        """
        """
        if isinstance(obj, bool):
            return True
        return SchemaContext.is_produced(obj)

    def produce(self):
        """
        """
        if self.is_produced(self._obj):
            return self._obj
        else:
            return AdditionalPropertiesContext._TmpObj(self)

    def parse(self, obj=None):
        """
        """
        if obj == None:
            self._obj = True
        elif isinstance(obj, bool):
            self._obj = obj
        else:
            tmp = {'t': {}}
            with SchemaContext(tmp, 't') as ctx:
                ctx.parse(obj)

            self._obj = tmp['t']


# self-reference 
setattr(SchemaContext, '__swagger_child__', {
    # items here should refer to an Schema Object.
    # refer to https://github.com/swagger-api/swagger-spec/issues/165
    # for details
    'items': (None, SchemaContext),
    'properties': (ContainerType.dict_, SchemaContext),
    # solution for properties with 2 possible types
    'additionalProperties': (None, AdditionalPropertiesContext),
    'allOf': (ContainerType.list_, SchemaContext),
})



class ParameterContext(Context):
    """ Context of Parameter Object, along with
    Reference Object
    """

    __swagger_child__ = {
        'schema': (None, SchemaContext),
        # items here should refer to an Items Object.
        # refer to https://github.com/swagger-api/swagger-spec/issues/165
        # for details
        'items': (None, ItemsContext),
    }
    __swagger_ref_object__ = Parameter


class HeaderContext(Context):
    """ Context of Header Object
    """

    __swagger_child__ = {
        'items': (None, ItemsContext),
    }
    __swagger_ref_object__ = Header


class ResponseContext(Context):
    """ Context of Response Object
    """

    __swagger_child__ = {
        'schema': (None, SchemaContext),
        'headers': (ContainerType.dict_, HeaderContext),
    }
    __swagger_ref_object__ = Response


class OperationContext(Context):
    """ Context of Operation Object
    """

    __swagger_child__ = {
        'parameters': (ContainerType.list_, ParameterContext),
        'responses': (ContainerType.dict_, ResponseContext),
    }
    __swagger_ref_object__ = Operation


class PathItemContext(Context):
    """ Context of Path Item Object
    """

    __swagger_child__ = {
        'get': (None, OperationContext),
        'put': (None, OperationContext),
        'post': (None, OperationContext),
        'delete': (None, OperationContext),
        'options': (None, OperationContext),
        'head': (None, OperationContext),
        'patch': (None, OperationContext),
        'parameters': (ContainerType.list_, ParameterContext),
    }
    __swagger_ref_object__ = PathItem


class SecuritySchemeContext(Context):
    """ Context of Security Schema Object
    """

    __swagger_ref_object__ = SecurityScheme



class TagContext(Context):
    """ Context of Tag Object
    """

    __swagger_ref_object__ = Tag
    __swagger_child__ = {
        'externalDocs': (None, ExternalDocumentationContext),
    }


class ContactContext(Context):
    """ Context of Contact Object
    """

    __swagger_ref_object__ = Contact


class LicenseContext(Context):
    """ Context of License Object
    """

    __swagger_ref_object__ = License


class InfoContext(Context):
    """ Context of Info Object
    """

    __swagger_ref_object__ = Info
    __swagger_child__ = {
        'contact': (None, ContactContext),
        'license': (None, LicenseContext),
    }


class SwaggerContext(Context):
    """ Context of Swagger Object
    """

    __swagger_child__ = {
        'info': (None, InfoContext),
        'paths': (ContainerType.dict_, PathItemContext),
        'definitions': (ContainerType.dict_, SchemaContext),
        'parameters': (ContainerType.dict_, ParameterContext),
        'responses': (ContainerType.dict_, ResponseContext),
        'securityDefinitions': (ContainerType.dict_, SecuritySchemeContext),
        'tags': (ContainerType.list_, TagContext),
        'externalDocs': (None, ExternalDocumentationContext),
    }
    __swagger_ref_object__ = Swagger
