pyswagger
=========

[![Build Status](https://travis-ci.org/AntXlab/pyswagger.svg?branch=master)](https://travis-ci.org/AntXlab/pyswagger)
[![Coverage Status](https://coveralls.io/repos/AntXlab/pyswagger/badge.png?branch=master)](https://coveralls.io/r/AntXlab/pyswagger?branch=master)

A python client for [Swagger](https://helloreverb.com/developers/swagger) enabled REST API,

- [Features](https://github.com/AntXlab/pyswagger/blob/master/README.md#features)
- [Quick Start](https://github.com/AntXlab/pyswagger/blob/master/README.md#quick-start)
- [Reference](https://github.com/AntXlab/pyswagger/blob/master/README.md#reference)
- [Development](https://github.com/AntXlab/pyswagger/blob/master/README.md#development)
- [FAQ](https://github.com/AntXlab/pyswagger/blob/master/README.md#faq)

---------

##Features
- support swagger **1.2**(not yet)
- suppoer python **2.6**, **2.7**, **3.3**, **3.4**
- type safe, input/output are converted according to [Data Type](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#43-data-types) described in swagger.
- builtin client implementation based on various http clients.
  - [requests](https://github.com/kennethreitz/requests)
  - [tornado.httpclient.AsyncHTTPClient](http://tornado.readthedocs.org/en/latest/httpclient.html)


##Quick Start

##Reference

###Installation
###SwaggerApp
###SwaggerAuth
###SwaggerClient

##Development
env preparation
```bash
pip install -r requirement-dev.txt
```

unit testing
```bash
python -m pytest -s -v --cov=pyswagger --cov-config=.coveragerc --cov-report=html pyswagger/tests
```

##FAQ
- Format of date-time and date?
  - The preferred way is [json schema](http://xml2rfc.ietf.org/public/rfc/html/rfc3339.html#anchor14) according to this [issue](https://github.com/wordnik/swagger-spec/issues/95)
- Format of byte?
  - The way to encode/decode byte is [base64](https://github.com/wordnik/swagger-spec/issues/50).

