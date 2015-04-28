Holder/Dispatcher for user-provided authorization info. Initialize this object like **SwaggerSecurity(app)**, where **app** is an instance of SwaggerApp. To add authorization, call **SwaggerSecurity.update\_with(name, token)**, where **name** is the name of Authorizations object in Swagger 1.2(Security Scheme Object in Swagger 2.0) , and **token** is different for different kinds of authorizations:
- basic authorization: (username, password)
- api key: the api key
- oauth2: the access\_token


