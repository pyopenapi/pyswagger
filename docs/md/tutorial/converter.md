### Converting a Document

pyswagger could be used as a forward converter: loading a Swagger document in older version, and dump it into a newer version.

```python
from pyswagger import SwaggerApp
import json
import yaml
# load a document in Swagger 1.2
app = SwaggerApp.create('/path/to/your/resource/file/resource_list.json')
# dump root object(Swagger Object) in Swagger 2.0 into a dict
obj = app.dump()

# save as a JSON file
with open('./swagger.json', 'w') as w:
    w.write(json.dumps(obj, indent=2))

# save as a YAML file
with open('./swagger.yaml', 'w') as w:
    w.write(yaml.dump(obj))
```

## What's missed when converting from Swagger 1.2

There are inconsistency between Swagger 1.2 and 2.0.

### 'collectionFormat' is used instead of 'allowMultiple', below is an example of conversion.

```json
{
    "allowMultiple":true,
    "type":"string",
    "enum":[
        "available",
        "pending",
        "sold"
    ]
}
```

would be converted to

```json
{
    "collectionFormat":"csv",
    "items":{
        "type":"string",
        "enum":["available", "pending", "sold"]
    }
}
```

Notice that array is used instead of 'allowMultiple'.

### basePath

Multiple basePath(s) are allowed in Swagger 1.2, however, only one is allowed in Swagger 2.0. If you define different basePath in resource files, pyswagger would raise an Exception and refuse to proceed.

### Migration Guide

For more information, refer to [migration guide](https://github.com/swagger-api/swagger-spec/wiki/Swagger-1.2-to-2.0-Migration-Guide).

