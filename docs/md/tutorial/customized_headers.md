## Customized Headers when making requests

Sometimes you need to add customized headers that are not listed in OpenAPI specs,
you can get this done in this way:

```python
from pyswagger import App
from pyswagger.contrib.client.requests import Client

app = App.create('http://petstore.swagger.io/v2/swagger.json')
client = Client()

# provide a header
client.request(
    app.op['getUserByName'](username='Tom'),
    headers={'MY-TEST-HEADER': '123'}
)

# headers with multiple value to one key
client.request(
    app.op['getUserByName'](username='Tom'),
    headers=[('MY-TEST-HEADER', '123'), ('MY-TEST-HEADER', '456')],
)

# headers with multiple value to one key, and join them by comma
client.request(
    app.op['getUserByName'](username='Tom'),
    headers=[('MY-TEST-HEADER', '123'), ('MY-TEST-HEADER', '456')],
    opt={'join_headers': True}
)
```

