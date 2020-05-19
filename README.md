# pytangle
python wrapper for crowdtangle 

Copy config_sample.json into a file named config.json. Edit at least your API token.

Python 3.3 and up. Tested on 3.7.

- `connectivity.py`: uses requests to forward calls to the api endpoints. performs rate limiting and network-related error handling.
- `api.py`: object oriented and functional interfaces to the api
- `utils.py`: common utility procedures
- `pytangle.py`: main file with examples
