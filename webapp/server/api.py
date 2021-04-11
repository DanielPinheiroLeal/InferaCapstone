'''
App backend API
'''
import argparse
from pathlib import Path
import atexit
from flask import Flask, jsonify, request, redirect, make_response
from flask_cors import CORS
import numpy as np
import database
from sklearn.manifold import TSNE

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model-path", help="Path to directory containing saved topic modelling files", required=True)
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
    Main search route. Looks for URL query string "author", "title", "id", or "topic". If querying
    by author, title, or id, also requires additional query string "mode" as "exact" or "related".

    Search examples:
      author: http://localhost:5000/search?author=Jane%20Doe%201000&mode=exact
      title: http://localhost:5000/search?title=Phasor%20Neural%20Networks&mode=exact
      id: http://localhost:5000/search?id=0&mode=exact
      topic: http://localhost:5000/search?topic=reinforcement%20learning
    '''
    author = request.args.get('author')
    title = request.args.get('title')
    paper_id = request.args.get('id')
    topic = request.args.get('topic')
    mode = request.args.get('mode')

    if author:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for author search"), 400
        res = db.query_by_author(author, mode)

        if args.debug:
            res, query_time = res

    elif title:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for title search"), 400
        res = db.query_by_title(title, mode)

        if args.debug:
            res, query_time = res

    elif paper_id:
        if not mode:
            return jsonify("[ERROR]: 'mode' query string required for id search"), 400
        res = db.query_by_paper_id(int(paper_id), mode)

        if args.debug:
            res, query_time = res

    elif topic:
        res = db.query_by_string(topic)

        if args.debug:
            res, query_time = res

    else:
        return jsonify("[ERROR]: missing or incorrect URL query arguments"), 400

    return jsonify(res)

@app.route('/article/pdf_by_path/<pdf_path>')
def article_pdf_by_path(pdf_path):
    '''
    Serve PDF files from the file system based on PDF path in file system.

    Parameters:
        pdf_path: Full file system path to PDF file. E.g., `C:\\pdf_files\\file1.pdf`

    Example: http://localhost:5000/article/pdf_by_path/C%3A%5C%5Cpdf_files%5C%5Cfile1.pdf
    '''
    title = Path(pdf_path).stem

    try:
        with open(pdf_path, "rb") as pdf:
            pdf_bytes = pdf.read()
    except Exception as err:
        return jsonify("[ERROR]: {}".format(err)), 400

    res = make_response(pdf_bytes)
    res.headers['Content-Type'] = 'application/pdf'
    res.headers['Content-Disposition'] = 'inline; filename={}.pdf'.format(title)
    return res

@app.route('/article/pdf_by_id/<paper_id>')
def article_pdf_by_id(paper_id):
    '''
    Serve PDF files from the file system based on PDF id in database.

    Parameters:
        paper_id: PDF id in database

    Example: http://localhost:5000/article/pdf_by_id/Phasor_Neural_Networks
    '''
    db_res = db.query_by_paper_id(int(paper_id), "exact")
    if args.debug:
        db_res, query_time = db_res

    if not db_res:
        return jsonify("[ERROR]: could not find paper_id ({}) in database".format(paper_id)), 400

    with open(db_res[0]["pdf"], "rb") as pdf:
        pdf_bytes = pdf.read()
    res = make_response(pdf_bytes)
    res.headers['Content-Type'] = 'application/pdf'
    res.headers['Content-Disposition'] = 'inline; filename={}.pdf'.format(db_res[0]["title"])
    return res

@app.route('/article/pdf_by_title/<title>')
def article_pdf_by_title(title):
    '''
    Serve PDF files from the file system based on PDF title in database.

    Parameters:
        title: PDF title in database

    Example: http://localhost:5000/article/pdf_by_title/Phasor_Neural_Networks
    '''
    db_res = db.query_by_title(title, "exact")
    if args.debug:
        db_res, query_time = db_res

    if not db_res:
        return jsonify("[ERROR]: could not find title ({}) in database".format(title)), 400

    with open(db_res[0]["pdf"], "rb") as pdf:
        pdf_bytes = pdf.read()
    res = make_response(pdf_bytes)
    res.headers['Content-Type'] = 'application/pdf'
    res.headers['Content-Disposition'] = 'inline; filename={}.pdf'.format(title)
    return res

@app.route('/visualization/<id>')
def visualization(id):
    knn = db.query_by_paper_id(int(id), "related")

    coords = []
    for paper in knn:
        coords.append(paper["coord"])
    coords_numpy = np.array(coords)
    transformed = TSNE(n_components = 2).fit_transform(coords_numpy)

    for i, paper in enumerate(knn):
        paper["processed_coord"] = transformed[i].tolist()

    return jsonify(knn)

db = database.get_db(model_path=args.model_path, debug_info=args.debug) # persistent connection to database at app start
atexit.register(database.close_db, db) # close database connection at app exit
app.run()
