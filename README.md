pyswagger
=========

A python rest client for swagger enabled rest API, which integrated with different kinds of http clients,
ex. AsyncHTTPClient in tornado.

Here are **TODO**s:
- type check against [Data Type Fields](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#433-data-type-fields)
- resolve [$ref](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#dataTypeRef)
- support model inheritance. (refer to [subType](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#modelSubTypes) and [discriminator](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#modelDiscriminator))
- OAuth 2.0 support


##Contents
- [Development](https://github.com/AntXlab/pyswagger/edit/master/README.md)


---------


###Development
unit testing
```bash
python -m py.test -s -v --cov=pyswagger --cov-report=html pyswagger/tests
```
