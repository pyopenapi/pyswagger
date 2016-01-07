##Changes

###0.8.17

- (deprecated) implicit dereferencing
  ```json
  "definitions":{
    "User":{
    },
    "AuthorizedUser":{
      "$ref": "User"   --> deferenced to "#/definitions/User"
    }
  }
  ```
- __NEW__ relative file reference
  ```
  "definitions":{
    "User": {
      "$ref": "other_folder/User.json"
    }
  }
  ```
