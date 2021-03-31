# Server

Backend server in Python using Flask.

## Requirements

- Python 3.x
- Flask - `pip install flask`
- flask_cors - `pip install flask_cors`
- Neo4j (see PPD under Creation --> Database)

## How to start server

- Start neo4j database
- `python api.py`
    - Command line arguments:
        - `-d`, `--debug`: Optional. Set to `True` to turn on debug mode. Default: `False` \
        e.g. `python api.py -d True`

## Functionality

### Search

#### Author

Visit `http://localhost:5000/search?author=<AUTHOR>`, where `<AUTHOR>` is the author name of document(s) in the database. \
E.g., http://localhost:5000/search?author=Jane%20Doe%2010000&mode=exact

#### Title

Visit `http://localhost:5000/search?title=<TITLE>`, where `<TITLE>` is the title of a document in the database. \
E.g., http://localhost:5000/search?title=Consistent_Plug-in_Classifiers_for_Complex_Objectives_and_Constraints&mode=exact

#### Coordinates

Visit `http://localhost:5000/search?coords=<COORDS>`, where `<COORDS>` is a comma-separated list of coordinates similar to document coordinates in the database. \
E.g., http://localhost:5000/search?coords=66,39.4,11.2,4.9,17.9,-8.7,-27.4,3.5,2.3,0.3

### View PDF

#### Method 1

Visit `http://localhost:5000/article/pdf/<PDF_PATH>`, where `<PDF_PATH>` is the full file system path ending in `.pdf` to a PDF file, url-encoded (e.g. with https://meyerweb.com/eric/tools/dencoder/). \
E.g., `http://localhost:5000/article/pdf/C%3A%5Cpdf_files%5Cfile1.pdf` (for a PDF file at `C:\pdf_files\file1.pdf`)

#### Method 2

Visit `http://localhost:5000/article/pdf_by_title/<TITLE>`, where `<TITLE>` is the title of a document in the database. \
E.g., http://localhost:5000/article/pdf_by_title/Consistent_Plug-in_Classifiers_for_Complex_Objectives_and_Constraints
