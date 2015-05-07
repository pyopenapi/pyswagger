## Making a Request

Three parts are involved with making a request:
 - access the Operation object
 - provide parameters to the Operation object, it will return (SwaggerRequest, SwaggerResponse) pair
 - provide this pair to the client implementation you choose

### Access Operation
There are many ways to access an Operation object. For example, if you want to access 'getUserByName' in petstore.
```python
from pyswagger import SwaggerApp

app = SwaggerApp.create('http://petstore.swagger.io/v2/swagger.json')

# via operationId and tag, they are optional in swagger 2.0
op = app.op['getUserByName']         # when the operationId is unique
op = app.op['user', 'getUserByName'] # tag + operationId

# via JSON Pointer, every object in Swagger can be referenced via its JSON Pointer.
# The JSON pointer of Operation 'getUserByName' is '#/paths/~1user~1{username}/get',
# here we provide a simple way for you to handle JSON pointer.
from pyswagger import utils
# check the place of the Operation 'getUserByName' in petstore
op = app.resolve(utils.jp_compose(['#', 'paths', '/user/{username}', 'get']))

# cascade resolving
username_api = app.resolve(utils.jp_compose(['#', 'paths', '/user/{username}']))
op = username_api.resolve('get')
# there is no special character in 'get',
# just access it like a property
op = username_api.get
```

### Provide parameter
This step involves converting primitives in python to primitives in Swagger,
please refer to [here](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#data-types) for a list of primitives im Swagger.
```python
# a fake operation containing all types of primitives
op = app.op['FakeApi']

req_and_resp = op(
  # integer, long, 
  Id=1,
  # float, double
  speed=27.3,
  # string
  name='Tom',
  # byte
  raw=b'fffffffffff',
  # byte, in string, would be encoded to 'utf-8'
  raw_s='jdkjldkjlsdfs',
  # boolean
  like_suki=True,
  # date, datetime, in timestamp
  next_date_1=0.0,
  # date, in datetime.date
  next_date_2=datetime.date.today(),
  # datetime, in datetime.datetime
  next_date_3=datetime.datetime.now(),
  # date, in string ISO8601
  next_date_4='2007-04-05',
  # datetime, in string ISO8601
  next_date_5='2007-04-05T12:30:00-02:00',
  # array of integer
  list_of_ids=[1, 2, 3, 4, 5],
  # an object
  user=dict(id=1, username='Tom'),
  # list of objects
  users=[
    dict(id=1, username='Tom'),
    dict(id=2, username='Mary')
  ]
)
```
### Pass result to Client
The return value when calling an Operation is a pair of (SwaggerRequest, SwaggerResponse),
just pass it to 'request' function of client. Below is a full example of 'getUserByName'
```python
from pyswagger import SwaggerApp
from pyswagger.contrib.client.request import Client

app = SwaggerApp.create('/path/to/your/resource/file/swagger.json')
client = Client()

# make the request
response = client.request(
  app.op['getUserByName']( # access the Operation
    username='Tom'         # provide the parameter
  ))

```
