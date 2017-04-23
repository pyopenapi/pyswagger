pyswagger
=========

[![Build Status](https://travis-ci.org/mission-liao/pyswagger.svg?branch=master)](https://travis-ci.org/mission-liao/pyswagger)
[![Coverage Status](https://coveralls.io/repos/mission-liao/pyswagger/badge.svg?branch=master&style=flat)](https://coveralls.io/r/mission-liao/pyswagger?branch=master)

A python client for [Swagger](https://helloreverb.com/developers/swagger) enabled REST API. It wouldn't be easier to
try Swagger REST API by [Swagger-UI](https://github.com/wordnik/swagger-ui). However, when it's time to **unittest**
your API, the first option you find would be [Swagger-codegen](https://github.com/wordnik/swagger-codegen), but the better option is us.

This project is developed after [swagger-py](https://github.com/digium/swagger-py), which is a nicely implemented one, and inspired many aspects of this project. Another project is [flex](https://github.com/pipermerriam/flex), which focuses on parameter validation, try it if you can handle other parts by yourselves.

For other projects related to Swagger tools in python, check [here](https://github.com/swagger-api/swagger-spec#python).

**pyswagger** is much easier to use (compared to swagger-codegen, you don't need to prepare a scala environment) and tries hard to **fully supports** [Swagger Spec](https://helloreverb.com/developers/swagger) in all aspects.

Read the [Document](http://pyswagger.readthedocs.org/en/latest/), or just go through this README.

- [Features](README.md#features)
- [Tutorial](README.md#tutorial)
- [Quick Start](README.md#quick-start)
- [Installation](README.md#installation)
- [Reference](README.md#reference)
- [Contributors](README.md#contributors)
- [Contribution Guideline](README.md#contribution-guildeline)
- [FAQ](README.md#faq)
- [Changes](CHANGES.md)

---------

## Features
- **NEW** convert Swagger Document from older version to newer one. (ex. convert from 1.2 to 2.0)
- support Swagger **1.2**, **2.0** on python ~~2.6~~, **2.7**, **3.3**, **3.5**, **3.6**
- support YAML via [Pretty-YAML](https://github.com/mk-fg/pretty-yaml)
- support $ref to **External Document**, multiple swagger.json will be organized into a group of App. And external document with self-describing resource is also supported (refer to [issue](https://github.com/swagger-api/swagger-spec/issues/219)).
- type safe, input/output are converted to python types according to [Data Type](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#43-data-types) described in Swagger. You don't need to touch any json schema when using pyswagger. Limitations like **minimum/maximum** or **enum** are also checked. **Model inheritance** also supported.
- provide function **App.validate** to check validity of the loaded API definition according to spec.
- builtin client implementation based on various http clients in python. For usage of these clients, please refer to `pyswagger.tests.contrib.client` for details
  - [requests](https://github.com/kennethreitz/requests)
  - [tornado.httpclient.AsyncHTTPClient](http://tornado.readthedocs.org/en/latest/httpclient.html)
  - [flask.testing.FlaskClient](http://flask.pocoo.org/docs/0.10/api/#flask.testing.FlaskClient)
  - [webapp2](http://webapp2.readthedocs.io/en/latest/guide/testing.html)
- not implemented parts, fire me a bug if you need it
  - [ ] Swagger 2.0
    - [ ] Schema.pattern
    - [ ] Scheme.patternProperties
    - [ ] Schema.readonly
    - [ ] Schema.allowEmptyValue
    - [ ] A scanner to validate schema
  - [ ] A WebSocket client
  - [ ] dump extension field

---------

## Tutorial

- [Initialization](docs/md/tutorial/init.md)
- [Making a Request](docs/md/tutorial/request.md)
- [Access the Response](docs/md/tutorial/response.md)
- [Testing a Local Server](docs/md/tutorial/local.md)
- [Converting Document into another version](docs/md/tutorial/converter.md)
- [Exntending Primitive Factory for user-defined primitives](docs/md/tutorial/extend_prim.md)
- [Rendering Random Requests for BlackBox Testing](docs/md/tutorial/render.md)
- [Operation MIME Support](docs/md/tutorial/mime.md)
- [Test with Invalid Input](docs/md/tutorial/invalid.md)
- [Load Spec from a Restricted Service](docs/md/tutorial/restricted_service.md)

---------

## Quick Start

Before running this script, please make sure [requests](https://github.com/kennethreitz/requests) is installed on your environment.

```python
from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
from pyswagger.utils import jp_compose

# load Swagger resource file into App object
app = App._create_('http://petstore.swagger.io/v2/swagger.json')

auth = Security(app)
auth.update_with('api_key', '12312312312312312313q') # api key
auth.update_with('petstore_auth', '12334546556521123fsfss') # oauth2

# init swagger client
client = Client(auth)

# a dict is enough for representing a Model in Swagger
pet_Tom=dict(id=1, name='Tom', photoUrls=['http://test']) 
# a request to create a new pet
client.request(app.op['addPet'](body=pet_Tom))

# - access an Operation object via App.op when operationId is defined
# - a request to get the pet back
pet = client.request(app.op['getPetById'](petId=1)).data
assert pet.id == 1
assert pet.name == 'Tom'

# new ways to get Operation object corresponding to 'getPetById'.
# 'jp_compose' stands for JSON-Pointer composition
pet = client.request(app.resolve(jp_compose('/pet/{petId}', base='#/paths')).get(petId=1)).data
assert pet.id == 1
```

---------

## Installation
We support pip installtion.
```bash
pip install pyswagger
```

Additional dependencies must be prepared before firing a request. If you are going to access a remote/local web server, you must install [requests](https://github.com/kennethreitz/requests) first.
```bash
pip install requests
```

If you want to test a local tornado server, please make sure tornado is ready on your environment
``` bash
pip install tornado
```

We also provide native client for flask app, but to use it, flask is also required
``` bash
pip install flask
```


---------

## Reference
All exported API are described in following sections. ![A diagram about relations between components](https://docs.google.com/drawings/d/1DZiJgl4i9L038UJJp3kpwkWRvcNQktf5h-e4m96_C-k/pub?w=849&h=530)

- [App](docs/md/ref/app.md)
- [SwaggerClient](docs/md/ref/client.md)
- [Security](docs/md/ref/security.md)

---------

## Contributors
- [Marcin Goliński](https://github.com/mjgolinski)
- [Andrey Mikhailov](https://github.com/zlovred)
- [Telepenin Nikolay](https://github.com/prefer)
- [WangJiannan](https://github.com/WangJiannan)

---------

## Contribution Guildeline
report an issue:
- issues can be reported [here](https://github.com/mission-liao/pyswagger/issues)
- include swagger.json if possible
- turn on logging and report with messages on console
```python
import logging
logger = logging.getLogger('pyswagger')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)

logger.addHandler(console)
logger.setLevel(logging.DEBUG)

... your stuff

```

- describe expected behavior, or more specific, the input/output

request a merge
- try not to decrease the coverage rate
- test included

env preparation
```bash
pip install -r requirement-dev.txt
```

unit testing
```bash
python -m pytest -s -v --cov=pyswagger --cov-config=.coveragerc pyswagger/tests
```

---------

## FAQ
- Format of byte?
  - The way to encode/decode byte is [base64](https://github.com/wordnik/swagger-spec/issues/50).
- Format of datetime on the wire?
  - should be an ISO8601 string, according to this [issue](https://github.com/wordnik/swagger-spec/issues/95).
- How **allowMultiple** is handled?
  - Take type integer as example, you can pass ~~an integer or~~ an array/tuple of integer for this parameter. (a single value is no longer supported)
- What do we need to take care of when upgrading from Swagger 1.2 to 2.0?
  - **allowMultiple** is no longer supported, always passing an array even with a single value.
  - 'different host for different resource' is no longer supported in Swagger 2.0, only one host and one basePath is allowed in one swagger.json.
  - refer to [Migration Guide](https://github.com/swagger-api/swagger-spec/wiki/Swagger-1.2-to-2.0-Migration-Guide) from Swagger team.
  - The name of body parameters is no longer included in requests, refer to this [issue](https://github.com/mission-liao/pyswagger/issues/13) for details.
