Load Spec from a Restricted Service
=========

For services that are only accessible with some authorization, you'll need to authenticate yourself when loading resource from there. The default getter of pyswagger to load resource is only valid for public service. Refer to this [issue](https://github.com/mission-liao/pyswagger/issues/107) for more details.

You can make a CustomGetter by yourself, or provide a callback to SimpleGetter ( a little simpler, :) )
```python
from pyswagger.getter import SimpleGetter

# use any library you like, for example, the beautiful 'requests' library
import requests

def my_load(url):
    # prepare your auth info
    your_header_with_auth_info = {...}

    # make a request
    resp = requests.post('xxx', headers=your_header_with_auth_info, verify=False)
    if resp.statuc_code is 200:
        # return the raw string
        return resp.text
    else:
        raise Exception('something not ok')
```
