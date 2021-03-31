'''
App backend API
'''
import argparse
import atexit
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import database
import numpy as np
import matplotlib as mplt

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="Whether to turn debug mode on or off. True/False", required=False, default=False)
args = parser.parse_args()

app = Flask(__name__)
CORS(app)
if args.debug:
    app.config["DEBUG"] = True

@app.route('/')
def home():
    return redirect('/search')

@app.route('/search')
def search():
    '''
    Main search route. Looks for URL query string "author", "title", or
    "coords". If querying by author or title, also requires
    additional query string "mode" as "exact" or "related".

    Search examples:
      author: http://localhost:5000/search?author=Jane%20Doe%2010000&mode=exact
      title: http://localhost:5000/search?title=Paper%2010000&mode=related
      coordinates: http://localhost:5000/search?coords=0.6,0.7,0.1
    '''
    author = request.args.get('author')
    title = request.args.get('title')
    coords = request.args.get('coords')
    mode = request.args.get('mode')

    if author:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for author search")
        res = db.query_by_author(author, mode)

    elif title:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for title search")
        res = db.query_by_title(title, mode)

        knn = db.query_by_coord(res[0]["coord"])

        coords = []
        for paper in knn:
            coords.append(paper["coord"])
        coords_numpy = np.array(coords)
        pca = mplt.mlab.PCA(coords_numpy)
        projection = pca.project(coords_numpy)
        result = projection[:, :2]

        



    elif coords:
        coords = list(map(float, coords.split(','))) # convert comma separated string to list of floats
        res = db.query_by_coord(coords)

    else:
        return jsonify("[ERROR]: missing or incorrect URL query arguments")

    return jsonify(res)

db = database.get_db(debug_info=args.debug) # persistent connection to database at app start
atexit.register(database.close_db, db)
app.run()
