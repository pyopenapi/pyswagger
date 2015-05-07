## Initialzation

The first step to use pyswagger is creating a pyswagger.SwaggerApp object. You need to provide the path of the resource file. For example, a SwaggerApp for petstore can be initialized in this way:
```python
from pyswagger import SwaggerApp

# utilize SwaggerApp.create
app = SwaggerApp.create('http://petstore.swagger.io/v2/swagger.json')
```

## Initailize with A Local file

The path could be an URI or a absolute path. For example, a path /home/workspace/local/swagger.json could be passed like:
```python
from pyswagger import SwaggerApp

# file URI
app = SwaggerApp.create('file:///home/workspace/local/swagger.json')
# with hostname
app = SwaggerApp.create('file://localhost/home/workspace/local/swagger.json')
# absolute path
app = SwaggerApp.create('/home/workspace/local/swagger.json')
# without the file name, because 'swagger.json' is a predefined name
app = SwaggerApp.create('/home/workspace/local')
```
