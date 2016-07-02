## Make your own primitive creater

In pyswagger, there is a module designed to convert primitives in python to primitives in Swagger.
We already support those primitives defined in Swagger spec, for user-defined primitives, we provide a
way for users to provide primitives creater.

Here is a simple example for primitive creater:
```python
from pyswagger import App
from pyswagger.primitives import Primitive

# define your primitive handler
def encode_int(obj, val, ctx):
    # val is the value used to create this primitive, for example, a
    # dict would be used to create a Model and list would be used to
    # create an Array

    # obj in the spec used to create primitives, they are
    # Header, Items, Schema, Parameter in Swagger 2.0.

    # ctx is parsing context when producing primitives. Some primitves needs
    # multiple passes to produce(ex. Model), when we need to keep some globals
    # between passes, we should place them in ctx

    # a very simple encoding by minusing one.
    return int(val) - 1

# create a cusomized primitive factory
factory = Primitive()
# type == 'integer'
# format == 'encoded'
factory.register('integer', 'encoded', encode_int)

# init App with customized primitive factory
app = App.load(url, prim=factory)
```

There are cases the a primitive-creation needs multipl pass, you will need
_2nd_pass in those cases. Now it's only used when pyswagger creates Model and Array.

