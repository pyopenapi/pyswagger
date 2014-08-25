pyswagger
=========

[![Build Status](https://travis-ci.org/AntXlab/pyswagger.svg?branch=master)](https://travis-ci.org/AntXlab/pyswagger)
[![Coverage Status](https://coveralls.io/repos/AntXlab/pyswagger/badge.png?branch=master)](https://coveralls.io/r/AntXlab/pyswagger?branch=master)

A python REST client for swagger enabled rest API, which integrated with different kinds of http clients,
ex. AsyncHTTPClient in tornado. For me, the use case is to unittest a torando REST server.

Here are **TODO**s:
- support model inheritance. (refer to [subType](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#modelSubTypes) and [discriminator](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#modelDiscriminator))
- limitation checking
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
- those limitation defined in spec are checked during loading json.
  - the model of '$ref' really exist.
  - either '$ref' or 'type' exist for [Data Type Fields](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#433-data-type-fields)
  - items only exist when type is 'array'.
  - convert [Data Type Fields](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#433-data-type-fields) from string to right type.
  - those urls are syntax-checking before usage.
- tested, and welcome for pushing new suite of testing json files.

###Development
env preparation
```bash
pip install -r requirement-dev.txt
```

unit testing
```bash
python -m py.test -s -v --cov=pyswagger --cov-config=.coveragerc --cov-report=html pyswagger/tests
```

###FAQ
- Thread safe?
  - SwaggerApp is readonly and stateless -> safe, SwaggerClient is not.
- Format of date-time and date?
  - The preferred way is [json schema](http://xml2rfc.ietf.org/public/rfc/html/rfc3339.html#anchor14) according to this [issue](https://github.com/wordnik/swagger-spec/issues/95)
