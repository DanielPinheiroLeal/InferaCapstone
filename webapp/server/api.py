'''
App backend API
'''
import argparse
from pathlib import Path
import atexit
from flask import Flask, jsonify, request, redirect, make_response
from flask_cors import CORS
import database
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model-path", help="Path to directory containing saved model files", required=True)
parser.add_argument("-d", "--debug", help="Whether to turn debug mode on or off. True/False", required=False, default=False)
args = parser.parse_args()
app = Flask(__name__)
CORS(app)
if args.debug:
    app.config["DEBUG"] = True

@app.route('/')
def home():
    return redirect('/search'), 301

@app.route('/search')
def search():
    '''
    Main search route. Looks for URL query string "author", "title", or "topic". If querying by
    author or title, also requires additional query string "mode" as "exact" or "related".

    Search examples:
      author: http://localhost:5000/search?author=Jane%20Doe%2010000&mode=exact
      title: http://localhost:5000/search?title=Consistent_Plug-in_Classifiers_for_Complex_Objectives_and_Constraints&mode=exact
      topic: http://localhost:5000/search?topic=reinforcement%20learning
    '''
    author = request.args.get('author')
    title = request.args.get('title')
    topic = request.args.get('topic')
    mode = request.args.get('mode')
    viz = request.args.get('viz')

    if author:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for author search"), 400
        res = db.query_by_author(author, mode)

        if args.debug:
            res, query_time = res

    elif title:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for title search"), 400
        print("Getting by title: "+title)
        res = db.query_by_title(title, mode)

        if args.debug:
            res, query_time = res

    elif viz:
        res = db.query_by_title(title, "exact")
        knn = db.query_by_title(title, "related")

        coords = []
        for paper in knn:
            coords.append(paper["coord"])
        coords_numpy = np.array(coords)
        white_coords = (coords_numpy - coords_numpy.mean(axis=0)) / coords_numpy.std(axis=0)
        u, s, vh = np.linalg.svd(white_coords)
        projected_data = np.dot(white_coords, np.transpose(vh[:2]))

        for i, paper in enumerate(knn):
            paper["processed_coord"] = projected_data[i].tolist()
        knn.append(res) #the last knn entry is guaranteed to be the search result

        res = knn

    elif topic:
        res = db.query_by_string(topic)

        if args.debug:
            res, query_time = res

    else:
        return jsonify("[ERROR]: missing or incorrect URL query arguments"), 400

    return jsonify(res)

@app.route('/article/pdf/<pdf_path>')
def article_pdf(pdf_path):
    '''
    Serve PDF files from the file system based on PDF path in file system.

    Parameters:
        pdf_path: Full file system path to PDF file. E.g., `C:\\pdf_files\\file1.pdf`

    Example: http://localhost:5000/article/pdf/C%3A%5C%5Cpdf_files%5C%5Cfile1.pdf
    '''
    title = Path(pdf_path).stem

    with open(pdf_path, "rb") as pdf:
        pdf_bytes = pdf.read()
    res = make_response(pdf_bytes)
    res.headers['Content-Type'] = 'application/pdf'
    res.headers['Content-Disposition'] = 'inline; filename={}.pdf'.format(title)
    return res

@app.route('/article/pdf_by_title/<title>')
def article_pdf_by_title(title):
    '''
    Serve PDF files from the file system based on PDF title in database.

    Parameters:
        title: PDF title in database

    Example: http://localhost:5000/article/pdf_by_title/Consistent_Plug-in_Classifiers_for_Complex_Objectives_and_Constraints
    '''
    res = db.query_by_title(title, "exact")
    if args.debug:
        res, query_time = res

    with open(res[0]["pdf"], "rb") as pdf:
        pdf_bytes = pdf.read()
    res = make_response(pdf_bytes)
    res.headers['Content-Type'] = 'application/pdf'
    res.headers['Content-Disposition'] = 'inline; filename={}.pdf'.format(title)
    return res

db = database.get_db(model_path=args.model_path, debug_info=args.debug) # persistent connection to database at app start
atexit.register(database.close_db, db) # close database connection at app exit
app.run()
