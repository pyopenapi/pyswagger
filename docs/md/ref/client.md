You also need **SwaggerClient(security=None)** to access API, this layer wraps the difference between those http libraries in python. where **security**(optional) is `Security`, which helps to handle authorizations of each request.

```python
client.request(app.op['addPet'](body=dict(id=1, name='Tom')))
```
To make a request, you need to create a pair of request/response from **App.op** by providing essential parameters. Then passing the tuple of (request, response) to **SwaggerClient.request(req_and_resp, opt={})** likes the code segment above. Below is a reference mapping between python objects and Swagger primitives. Check this mapping when you need to construct a parameter set:
- **dict** corresponds to _Model_
- **list** corresponds to _Array_
- **datetime.datetime**, timestamp(float or int), or ISO8601-string for _date-time_ and _date_
- email is supported by providing a valid email in string
- **uuid.UUID**, uuid-string in hex, byte for _uuid_
- _File_ type is a little bit complex, but just similar to [request](https://github.com/kennethreitz/requests), which uses a dict containing file info.
```python
YouFile = {
  # header values used in multipart/form-data according to RFC2388
  'header': {
    'Content-Type': 'text/plain',
    
    # according to RFC2388, available values are '7bit', '8bit', 'binary'
    'Content-Transfer-Encoding': 'binary'
  },
  'filename': 'a.txt',
  'data': None (or any file-like object)
}
```
- other primitives are similar to python's primitives

To select a scheme(ex. 'http' or 'https') when making a request, just use **Request.scheme** property
```python
req, resp = operation(parameter1='test1')
req.scheem = 'http'
```

The return value is a **Response** object, with these attributes:
- status
- data, corresponds to Operation object's return value, or `ResponseMessage` object's _responseModel_ (in Swagger 1.2, `Schema` object of `Response` object in Swagger 2.0) when its status matched.
- header, organized in ```{key: [value1, value2...]}```
- message, corresponds to ResponseMessage object's _message_ when status matched on ResponseMessage object.
- raw, raw data without touching.


