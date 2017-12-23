### FAQ

#### Format of byte?

The way to encode/decode byte is [base64](https://github.com/wordnik/swagger-spec/issues/50).

#### Format of datetime on the wire?

should be an ISO8601 string, according to this [issue](https://github.com/wordnik/swagger-spec/issues/95).


#### How **allowMultiple** is handled?

Take type integer as example, you can pass ~~an integer or~~ an array/tuple of integer for this parameter. (a single value is no longer supported)

#### What do we need to take care of when upgrading from Swagger 1.2 to 2.0?

 - **allowMultiple** is no longer supported, always passing an array even with a single value.
 - 'different host for different resource' is no longer supported in Swagger 2.0, only one host and one basePath is allowed in one swagger.json.
 - refer to [Migration Guide](https://github.com/swagger-api/swagger-spec/wiki/Swagger-1.2-to-2.0-Migration-Guide) from Swagger team.
 - The name of body parameters is no longer included in requests, refer to this [issue](https://github.com/mission-liao/pyswagger/issues/13) for details.
