pyswagger
=========

A python REST client for swagger enabled rest API, which integrated with different kinds of http clients,
ex. AsyncHTTPClient in tornado. For me, the use case is to unittest a torando REST server.

Here are **TODO**s:
- [Data Type Fields](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#433-data-type-fields)
- resolve [$ref](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#dataTypeRef)
- support model inheritance. (refer to [subType](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#modelSubTypes) and [discriminator](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#modelDiscriminator))
- API-key and basic-auth
- OAuth 2.0 support with oauthlib
- Python 3 support


##Contents
- [Features](https://github.com/AntXlab/pyswagger/edit/master/README.md#features)
- [Development](https://github.com/AntXlab/pyswagger/edit/master/README.md#development)
- [FAQ](https://github.com/AntXlab/pyswagger/edit/master/README.md#faq)

---------

###Features
- support swagger **1.2**(not yet)
- idenpendent of http client, and provide a set of wrappers for common http clients.
- every property is wrapped in @property, make it readonly
- tested, and welcome for pushing new suite of testing json files.

###Development
env preparation
```bash
pip install -r requirement-dev.txt
```

unit testing
```bash
python -m py.test -s -v --cov=pyswagger --cov-report=html pyswagger/tests
```

###FAQ
- Thread safe?
  - SwaggerApp is readonly and stateless -> safe, SwaggerClient is not.
