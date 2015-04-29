## Testing a Local Server

As a backend developer, you will need to test your API before shipping. We provide a simple way to patch the url before client actually making a request

```python
from pyswagger import SwaggerApp
from pyswagger.contrib.client.request import Client

# create a SwaggerApp with a local resource file
app = SwaggerApp.create('/path/to/your/resource/file/swagger.json')
# init the client
client = Client()

# try to making a request
client.request(
  app.op['getUserByName'](username='Tom'),
  opt=dict(
    url_netloc='localhost:8001' # patch the url of petstore to localhost:8001
  ))
```
