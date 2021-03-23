'''
App backend API
'''
import argparse
import atexit
from flask import Flask, jsonify, request, redirect, url_for
import database

from flask_cors import CORS

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="Whether to turn debug mode on or off. True/False", required=False, default=False)
args = parser.parse_args()

app = Flask(__name__)
CORS(app)
if args.debug:
    app.config["DEBUG"] = True

@app.route('/')
def home():
    return redirect(url_for('search'))

@app.route('/search')
def search():
    '''
    Main search route. Looks for URL query string "author", "title", or
    coordinates "x", "y", "z". If querying by author or title, also requires
    additional query string "mode" as "exact" or "related".

    Search examples:
      author: http://localhost:5000/search?author=Jane%20Doe%2010000&mode=exact
      title: http://localhost:5000/search?title=Paper%2010000&mode=related
      coordinates: http://localhost:5000/search?x=0.6&y=0.7&z=0.1
    '''
    author = request.args.get('author')
    title = request.args.get('title')
    coords = [ request.args.get(coord, type=float) for coord in ('x', 'y', 'z') ]
    mode = request.args.get('mode')

    if author:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for author search")
        res = db.query_by_author(author, mode)

    elif title:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for title search")
        res = db.query_by_title(title, mode)

    elif all(coords):
        res = db.query_by_coord([coords[0], coords[1], coords[2]])

    else:
        return jsonify("[ERROR]: missing or incorrect URL query arguments")

    return jsonify(res)

db = database.get_db(debug_info=args.debug) # persistent connection to database at app start
atexit.register(database.close_db, db)
app.run()
