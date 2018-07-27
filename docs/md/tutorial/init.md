## Initialization

The first step to use pyswagger is creating a pyswagger.App object. You need to provide the path of the resource file. For example, a App for petstore can be initialized in this way:
```python
from pyswagger import App

# utilize App.create
app = App.create('http://petstore.swagger.io/v2/swagger.json')
```

## Initialize with a local file

The path could be an URI or a absolute path. For example, a path /home/workspace/local/swagger.json could be passed like:
```python
from pyswagger import App

# file URI
app = App.create('file:///home/workspace/local/swagger.json')
# with hostname
app = App.create('file://localhost/home/workspace/local/swagger.json')
# absolute path
app = App.create('/home/workspace/local/swagger.json')
# without the file name, because 'swagger.json' is a predefined name
app = App.create('/home/workspace/local')
```
