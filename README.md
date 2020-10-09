# `pytangle`
A python wrapper for crowdtangle 

### In this repository
- `pytangle.py`: main file with examples
- `pytangle/api.py`: object oriented interface to the api
- `pytangle/connectivity.py`: uses requests to forward calls to the api endpoints. performs rate limiting and network-related error handling.
- `pytangle/endpoints.py`: objects detailing the crowdtangle API endpoints 
- `pytangle/utils.py`: common utility procedures
- `pytangle_config_sample.json`: sample configuration file. `pytangle` uses this file to load your API token and to set logging 
preferences. Copy `pytangle_config_sample.json` into a file named `pytangle_config.json` before 
customizing it. You most likely want to edit at least your API token. See the later section for further customizations.      

### Quickstart
1. Install the package: `pip3 install pytangle`
2. Create a file named `pytangle_config.json` in the folder from where you will call `pytangle`, and paste: 
```json
{
  "token": "YOUR_CROWDTANGLE_TOKEN"
}
```
3. Check that everything works:
```python
from pytangle.api import API
api = API() # or "api = API(token=YOUR_CROWDTANGLE_TOKEN)" 
            # if you did not create pytangle_config.json

# fetch lists in the current dashboard
for a_list in api.lists():
   print(a_list)
```
### Installation
The quickest way to download and install is:

```bash
pip3 install pytangle
```

Otherwise, download the code, move into the directory, and install from the local file, e.g.:

```bash
git clone https://github.com/hide-ous/pytangle.git 
cd pytangle
pip3 install . 
```

To install only the dependencies, and use the library without installing,
run:

```bash
pip3 install -r requirements.txt
```

Python 3.5 and up. Tested on 3.7.


### Examples
It is easy to use the API. Just create an API instance, and start querying way. If you have customized `pytangle_config.json` the 
 API instance will automatically load your API token, otherwise you can assign explicitly via code. Rate limiting and 
 pagination are handled for you. 
   
```python
from pytangle.api import API
api = API()
# use the following line instead if you do not want to set up a configuration file
# api = API(token="YOUR_TOKEN") 
```

All query methods return an iterator, one result object (i.e. one post, account, ...) at a time. For example, to fetch 
the lists linked to the current dashboard:  
```python
from pytangle.api import API
api = API()
# fetch all lists linked to the current dashboard
for a_list in api.lists():
    print(a_list)
```

The same applies to other types of objects, like posts: 
```python
from pytangle.api import API
api = API()

# get the 5 top overperforming posts
for a_post in api.posts(count=5):
    print(a_post)
```

If you want information about a specific post, you can query it via either its facebook id or its crowdtangle id, by
specifying the `endpoint` (`platform` or `ct` respectively). For differences see 
[the official wiki](https://github.com/CrowdTangle/API/wiki/Posts#get-postid).
```python
from pytangle.api import API
api = API()

# get information about a specific post
post_id = "1515871602074952_5362226790772728"
for a_post in api.post(id=post_id, endpoint='platform'):
    print(a_post)
```

Get the leaderboard for the current dashboard:
```python
from pytangle.api import API
api = API()

# get the first 5 entries in the leaderboard for the current dashboard
for a_leaderboard in api.leaderboard(count=5):
    print(a_leaderboard)
```

Get the top 5 posts sharing a link (like in the crowdtangle chrome extension):
```python
from pytangle.api import API
api = API()

# get the top 5 sharers of a link
an_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
for a_post in api.links(count=5, link=an_url):
    print(a_post)
```

Get details about a specific account in a list:

```python
from pytangle.api import API
api = API()

# get information on an account
list_id = 12345 # the id of one of your lists
for an_account in api.accounts_in_list(count=5, listId=list_id):
    print(an_account)
```

Get all posts from a list in a specific date range (you can find which lists are in your dashboard via `api.lists()`:
```python
from pytangle.api import API
api = API()

# get all posts from a list from Jan until June 2020
list_ids = [12345, ] # ids of the lists of interest
for n, a_post in enumerate(api.posts(listIds=list_ids,
                                     count=-1,
                                     batchSize=100,
                                     sortBy='date',
                                     startDate='2020-01-01',
                                     endDate='2020-06-30',
                                     timeframe=None,
                                     )):
    # do something with the post
    if not n % 1000:
        print(n)
```
### Configuring `pytangle`

The configuration file `pytangle_config.json` is a simple json file, containing two main sections:
- `token`: is the API token associated with a dashboard within crowdtangle. If you have access to
 the API, you can locate your API token via your dashboard under Settings > API Access.  
- `logging`: is a dictionary of items determining how pytangle should log. It follows the conventions
in `logging.dictConfig`: for explanations on the various options see the 
[official reference](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details).

The default locations for `pytangle_config.json` are:
 - at the root of the presently used module, or 
 - in the user's home.
  
An API instance will attempt to load the token from the configuration file, if a token is not explicitly passed.
`pytangle.py` shows an example of how to initialize loggers using the configuration in `pytangle_config.json`. However, the API
will not load the logging configuration by default.

`pytangle_config_sample.json` provides a reasonable starting point to customize `pytangle`: just copy the file 
in one of the default locations under the name `pytangle_config.json`, and edit (at least) your `token`.

### Changelog
* 0.0.2 
    * bugfix: pass token via code instead of configuration file 
* 0.0.1 initial release
