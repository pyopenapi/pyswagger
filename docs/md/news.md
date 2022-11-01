### NEWs

Upcoming changes for OpenAPI 3.0 would be:

 - version changes to: `1.0.0`, if you need a stabler version, please use `pyswagger<1.0.0` in pip's requirement file.
 - most logic would be divided to this [repo](https://github.com/mission-liao/pyopenapi) and **pyswagger** would only contains code related to 'making requests' (just like what gophers did in [go-openapi](https://github.com/go-openapi))
 - **$ref** would not be normalized anymore. Every field from API spec would be left unchanged and create another field for patched version.
