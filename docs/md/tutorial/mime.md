## Operation MIME Support
Swagger operation may contain more than one MIME type.
pyswagger allows you to specify consume/produce MIME type when sending request.
Also, customized MIME codec is supported.

```python
from pyswagger import App
from pyswagger.contrib.client.requests import Client
from pyswagger.primitives import MimeCodec
import xmltodict
import dicttoxml


class XmlCodec:
    def marshal(self, value, **kwargs):  # name, _type, _format is available in kwargs
        name = kwargs['name']
        if name:
            return dicttoxml.dicttoxml(value, root=True, custom_root=name, attr_type=False)
        else:
            return '<?xml version="1.0" encoding="UTF-8" ?>' + dicttoxml.dicttoxml(value, root=False, attr_type=False)

    def unmarshal(self, data, **kwargs):  # name, _type, _format is available in kwargs
        return xmltodict.parse(data)


def _create_mime_codec():
    mime_codec = MimeCodec()
    xmlCodec = XmlCodec()
    for _type in ['application', 'text']:
        mime_codec.register('%s/xml' % _type, xmlCodec)
    return mime_codec


_mime_codec = _create_mime_codec()

app = App.load('http://petstore.swagger.io/v2/swagger.json', mime_codec=_mime_codec)
app.prepare(strict=True)
placeOrder = app.op['placeOrder']
body = dict(complete=True, id=1, petId=1, quantity=1)
client = Client()


def print_response(response):
    print 'status:', response.status
    print 'header:', response.header
    print 'raw:', response.raw
    print 'data:', response.data

print 'consumes:', placeOrder.consumes
print 'produces:', placeOrder.produces

# default consume 'application/json', produce: 'application/xml'
req, resp = placeOrder(body=body)
print_response(client.request((req, resp)))

# consume: 'application/xml'
req, resp = placeOrder(body=body)
req.consume('application/xml')
print_response(client.request((req, resp)))

# produce: 'application/json'
req, resp = placeOrder(body=body)
req.produce('application/json')
print_response(client.request((req, resp)))

# consume: 'application/xml', produce: 'application/json'
req, resp = placeOrder(body=body)
req.consume('application/xml').produce('application/json')
print_response(client.request((req, resp)))
```
