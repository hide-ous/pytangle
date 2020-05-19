# pytangle
python wrapper for crowdtangle 

Copy config_sample.json into a file named config.json. Edit At least your API token.

python 3.3 and up

- `connectivity.py`: uses requests to forward calls to the api endpoints. performs rate limiting and network-related error handling.
- `api.py`: object oriented and functional interface to the api
- `utils.py`: common utility procedures
- `pytangle.py`: main file with examples
