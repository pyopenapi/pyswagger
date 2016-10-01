### Test With Invalid Input

All you provided for **pyswagger.spec.v2_0.objects.Operation** would be inspected / validated based on the loaded Swagger (OpenAPI) spec. Therefore, when using pyswagger as an API client, this behavior is relevant, but it's just not required when you want to provide some invalid input for your own server.

Can those validation be skipped? No, but pyswagger allows you to patch them after "prepared". Taking an example from this [issue](https://github.com/mission-liao/pyswagger/issues/88)

```python
from pyswagger import App
from pyswagger.contrib.client.requests import Client

app = App._create_('http://petstore.swagger.io/v2/swagger.json')
client = Client()

pet_tom = dict(
    id=123,
    name='Tom',
    photoUrls='https://github.com/',
    status='available')                                                                                       

req, resp = app.op['addPet'](body=pet_tom) 

#  patching the "body" parameter named "body", ... which seems cumbersome
req._p['body']['body']['id'] = 'not_valid'

resp = client.request((req, resp,))                                                                            
print resp.status # the code I tried is 500, not 405
```

You can access those "prepared" parameters via **pyswagger.io.Request._p** property, it's a *dict*, which is arranging the parameters you provided by "type" and "name" defined in [OpenAPI spec](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#parameter-object). To be noted: when the name of "type" changed in later version of OpenAPI, **the key of _p would also be changed**.

