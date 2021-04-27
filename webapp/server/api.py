'''
App backend API
'''
import argparse
import atexit
from pathlib import Path
import urllib.parse
from flask import Flask, jsonify, request, redirect, make_response
from flask_cors import CORS
import numpy as np
from sklearn.manifold import TSNE
import database

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model-path", help="Path to directory containing saved topic modelling files", required=True)
parser.add_argument("-r", "--db-uri", help="Database URI", default="bolt://localhost:7687")
parser.add_argument("-u", "--user", help="Database account username", default="neo4j")
parser.add_argument("-p", "--password", help="Database account password", default="capstone")
parser.add_argument("-k", "--neighbours", help="Number of neighbours in knn graph", default=25, type=int)
parser.add_argument("-lsi", "--numLSI", help="Number of LSI dimensions", default=10, type=int)
parser.add_argument("-lda", "--numLDA", help="Number of LDA topics", default=10, type=int)
parser.add_argument("-pdf", "--pdf-path", help="Path to directory containing pdf files", default="")
parser.add_argument("-text", "--text-path", help="Path to directory containing text files", default="")
parser.add_argument("-t", "--train", help="Train the model from scratch. True/False", default=False, action="store_true")
parser.add_argument("-n", "--nodes", help="Rebuild database nodes. True/False", default=False, action="store_true")
parser.add_argument("-c", "--convert", help="Convert PDFs to text files", default=False, action="store_true")
parser.add_argument("-d", "--debug", help="Turn debug mode on or off. True/False", default=False, action="store_true")
args = parser.parse_args()

app = Flask(__name__)
CORS(app)

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

    pdf_path = urllib.parse.unquote(pdf_path)
    if pdf_path[0]=="\\":
        pdf_path = pdf_path.replace("\\","/")

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

@app.route('/visualization/<paper_id>')
def visualization(paper_id):
    itself = db.query_by_paper_id(int(paper_id), "exact")
    related = db.query_by_paper_id(int(paper_id), "related")
    if args.debug:
        itself, query_time = itself
        related, query_time = related
    knn = itself + related

    coords = []
    for paper in knn:
        coords.append(paper["coord"])
    coords_numpy = np.array(coords)
    transformed = TSNE(n_components = 2).fit_transform(coords_numpy)
    offset=transformed[0].tolist()
    for i, paper in enumerate(knn):
        pc =  transformed[i].tolist()
        pc[0]=pc[0]-offset[0]
        pc[1]=pc[1]-offset[1]
        paper["processed_coord"] = pc

    return jsonify(knn)

@app.route('/topicwords/<topic_id>')
def topic_terms(topic_id):
    topic_id=int(topic_id)
    if topic_id != -1:
        return jsonify(db.topic_terms[topic_id])
    else:
        return jsonify(db.topic_terms)

if __name__ == "__main__":
    if not args.pdf_path and (args.nodes or args.convert):
        raise RuntimeError("PDF path required `-pdf <path>` for options --nodes / --convert")
    if not args.text_path and (args.train or args.convert):
        raise RuntimeError("Text path required `-text <path>` for options --train / --convert")

    # persistent connection to database at app start
    db = database.get_db(
        uri=args.db_uri,
        user=args.user,
        password=args.password,
        num_neighbours=args.neighbours,
        lsi_dims=args.numLSI,
        lda_dims=args.numLDA,
        pdf_path=args.pdf_path,
        text_path=args.text_path,
        model_path=args.model_path,
        debug_info=args.debug,
        train_model=args.train,
        build_nodes=args.nodes,
        convert_pdfs=args.convert
    )

    # close database connection at app exit
    atexit.register(database.close_db, db)

    # start app
    app.run(debug=args.debug)
