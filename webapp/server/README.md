# Server

Backend server in Python using Flask.

## Requirements

- Python 3.x
- Flask - `pip install flask`
- Neo4j (see PPD under Creation --> Database)

## How to start server

- Start neo4j database
- `python api.py`
    - Command line arguments:
        - `-d`, `--debug`: Optional. Set to `True` to turn on debug mode. Default: `False` \
        e.g. `python api.py -d True`

## Examples

Try visiting the following URLs:
- http://localhost:5000/search?author=Jane%20Doe%2010000&mode=exact
- http://localhost:5000/search?title=Paper%2010000&mode=related
- http://localhost:5000/search?x=0.6&y=0.7&z=0.1
