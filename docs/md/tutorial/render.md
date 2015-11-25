## Rendering Random Requests for BlackBox Testing

pyswagger could be used to generate random inputs to test your own APIs. Below is an example to demonstrate such use-case. (note: this sample requires [request](https://github.com/kennethreitz/requests) ready on your environment)

```python
from pyswagger import SwaggerApp
from pyswagger.primitives import Renderer
from pyswagger.contrib.client.request import Client

# create a SwaggerApp with a local resource file
app = SwaggerApp.create('/path/to/your/resource/file/swagger.json')
# init client
cilent = Client()
# init renderer
renderer = Renderer()

# assume you have an Operation to test
input_ = renderer.render_all(
    app.s('user').post # the Operation
)
# this generated input could be passed to Operation.__call__,
# to get a pair of (SwaggerRequest, SwaggerResponse), or just
# pass them to client
resp = client.request(app.s('user').post(input_))
```

a _template_ could be provided in rendering options.
- 'object_template' could fix properties of rendered result for a Schema object.
- 'parameter_template' could fix parameters of rendered inputs for an Operation object.
```python
# assume you have 'email', 'password' to post a comment
renderer = Renderer()
opt = renderer.default()

# post a random blog with login info
# --------
# assume this Operation takes one body parameter,
# and the parameter corresponding to a Schema,
# with 'email', 'password', 'blog' properties...
op = app.s('blog').post
opt['object_template'].update({
    'email': test_email,
    'password': test_password
})
client.request(op(renderer.render_all(op, opt=opt)))

# update phone number of a user
# --------
# assume this Operation takes three query parameters: 'email', 'passwprd', and a random phone number...
op = app.s('user').update
opt['parameter_template'].update({
    'email': test_email,
    'password': test_password
})
client.request(op(renderer.render_all(op, opt=opt)))
```
