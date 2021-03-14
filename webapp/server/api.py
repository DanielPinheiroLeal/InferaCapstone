'''
App backend API
'''
import flask
import db

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.teardown_appcontext(db.close_db) # close db after every response

@app.route('/')
def home():
    return "Hello world!"

@app.route('/search')
def search():
    '''
    Main search route. Looks for URL query string "author", "title", or
    coordinates "x", "y", "z".

    Search examples:
      author: http://localhost:5000/search?author=Jane%20Doe%2010000
      title: http://localhost:5000/search?title=Paper%2010000
      coordinates: http://localhost:5000/search?x=0.6&y=0.7&z=0.1
    '''
    author = flask.request.args.get('author')
    title = flask.request.args.get('title')
    coords = [ flask.request.args.get(coord, type=float) for coord in ('x', 'y', 'z') ]

    if author:
        main_list, knn_list = db.get_db().query_by_author(author)
        return flask.jsonify(main_list, knn_list)
    elif title:
        main_list, knn_list = db.get_db().query_by_title(title)
        return flask.jsonify(main_list, knn_list)
    elif all(coords):
        knn_list = db.get_db().query_by_coord([coords[0], coords[1], coords[2]])
        return flask.jsonify(knn_list)
    else:
        return flask.jsonify("ERROR: missing or incorrect URL query arguments")

app.run()
