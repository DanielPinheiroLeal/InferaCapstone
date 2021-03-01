import flask
from test_neurips import DbDriver

app = flask.Flask(__name__)
app.config["DEBUG"] = True

db_driver = DbDriver("bolt://localhost:7687", "neo4j", "capstone", 100, r"H:\Saad\University\Course Material\Fourth Year\Semester 2\ESC472\Project\NeuripsSplit\NeurIPS", True)

@app.route('/')
def home():
    return "Hello world!"

# http://localhost:5000/author/Jane%20Doe%2010000
@app.route('/author/<author>')
def query_author(author):
    p1_list, p2_list = db_driver.query_by_author(author)
    if p1_list:
        return p1_list[0]
    elif p2_list:
        return p2_list[0]
    else:
        return "not found"

# http://localhost:5000/title/Paper%2010000
@app.route('/title/<title>')
def query_title(title):
    p1_list, p2_list = db_driver.query_by_title(title)
    if p1_list:
        return p1_list[0]
    elif p2_list:
        return p2_list[0]
    else:
        return "not found"

# http://localhost:5000/coord/0.6/0.7/0.1
@app.route('/coord/<x>/<y>/<z>')
def query_coord(x,y,z):
    p_list = db_driver.query_by_coord([float(x),float(y),float(z)])
    if p_list:
        return p_list[0], p_list[1]
    else:
        return "not found"

app.run()
