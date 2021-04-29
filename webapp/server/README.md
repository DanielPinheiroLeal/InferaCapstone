# Server

Backend server in Python using Flask.

## Requirements

- Python 3.x
- Flask - `pip install flask`
- flask_cors - `pip install flask_cors`
- Neo4j (see Section 4.2 (Quickstart Guide) in PPD)

## How to start server

- Start neo4j database
- Run `python api.py` with necessary command line arguments (see Section 4.2 (Quickstart Guide) in PPD)

## Functionality

### Search

#### Author

Visit `http://localhost:5000/search?author=<AUTHOR>`, where `<AUTHOR>` is the author name of document(s) in the database. \
E.g., http://localhost:5000/search?author=Jane%20Doe%2010000&mode=exact

#### Title

Visit `http://localhost:5000/search?title=<TITLE>`, where `<TITLE>` is the title of a document in the database. \
E.g., http://localhost:5000/search?title=Phasor%20Neural%20Networks&mode=exact

#### Paper ID

Visit `http://localhost:5000/search?id=<ID>`, where `<ID>` is the ID of a document in the database. \
E.g., http://localhost:5000/search?id=0&mode=exact

#### Topic

Visit `http://localhost:5000/search?topic=<TOPIC>`, where `<TOPIC>` is an arbitrary string that the model will convert to coordinates in latent semantic space. \
E.g., http://localhost:5000/search?topic=reinforcement%20learning

### View PDF

#### Method 1 - PDF Path

Visit `http://localhost:5000/article/pdf_by_path/<PDF_PATH>`, where `<PDF_PATH>` is the full file system path ending in `.pdf` to a PDF file, url-encoded (e.g. with https://meyerweb.com/eric/tools/dencoder/). \
E.g., `http://localhost:5000/article/pdf_by_path/C%3A%5Cpdf_files%5Cfile1.pdf` (for a PDF file at `C:\pdf_files\file1.pdf`)

#### Method 2 - Paper ID

Visit `http://localhost:5000/article/pdf_by_id/<ID>`, where `<ID>` is the ID of a document in the database. \
E.g., http://localhost:5000/article/pdf_by_id/0

## Visualization, Topic words

See Section 7.2 in PPD for more info.
