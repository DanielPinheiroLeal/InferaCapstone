'''
App backend database functions
'''
import time
import random
from pathlib import Path
from neo4j import GraphDatabase
from flask import g

def get_db(pdf_path="", num_neighbours=100):
    if "db" not in g:
        g.db = DbDriver("bolt://localhost:7687", "neo4j", "capstone", num_neighbours, pdf_path, True)
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(pdf_path, num_neighbours=100):
    db = get_db(pdf_path=pdf_path, num_neighbours=num_neighbours)
    db.build_db()
    db.build_knn_graph()

class DbDriver:

    # Connect to the DB
    def __init__(self, uri, user, password, numK, pdf_path, debug_info):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.graph_name = 'neuripsGraph' # Name of the GDS graph
        self.numK = numK # Number of neighbours for the KNN algorithm
        self.pdf_path = pdf_path # FS path to the PDF files (It will search for PDFs recursively starting here)
        self.debug_info = debug_info # Turn on/off debug messages

    # Close DB connection
    def close(self):
        self.driver.close()

    # Build the DB
    def build_db(self):
        if self.debug_info:
            t_init = time.perf_counter()

        print("\nBuilding database...\n")

        i = 0
        for path in Path(self.pdf_path).rglob('*.pdf'):
            pdf = str(path)
            author = "Jane Doe " + str(i) # Placeholder
            title = "Paper " + str(i) # Placeholder
            coord = [random.random(), random.random(), random.random()] # Placeholder
            self.insert_node(pdf, author, title, coord)
            i += 1

        if self.debug_info:
            t_final = time.perf_counter()

        print("\nDatabase successfully built! Number of papers: {}\n".format(i))

        if self.debug_info:
            print("(INFO): {:.3f} s elapsed".format(t_final - t_init))

    # Destroy the DB and GDS KNN graph (if any)
    def destroy_db(self):
        if self.debug_info:
            t_init = time.perf_counter()

        print("\nTearing down database...\n")

        with self.driver.session() as session:
            session.write_transaction(self._destroy_gds_graph, self.graph_name)
            session.write_transaction(self._destroy_db)

        if self.debug_info:
            t_final = time.perf_counter()

        print("\nDatabase successfully removed!\n")

        if self.debug_info:
            print("(INFO): {:.3f} s elapsed".format(t_final - t_init))

    # Insert a node (paper) in the graph database
    def insert_node(self, pdf, author, title, coord):
        with self.driver.session() as session:
            session.write_transaction(self._insert_node, pdf, author, title, coord)

    # Run the KNN algorithm in the DB nodes
    def build_knn_graph(self):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            # Destroy GDS graph if it exists
            session.write_transaction(self._destroy_gds_graph, self.graph_name)
            # Create GDS graph
            session.write_transaction(self._create_gds_graph, self.graph_name)
            print("\nCreated GDS graph\n")
            session.write_transaction(self._run_knn, self.graph_name, self.numK)
            print("\nKNN graph built\n")

        if self.debug_info:
            t_final = time.perf_counter()
            print("(INFO): {:.3f} s elapsed".format(t_final - t_init))

    # Query the DB by author
    def query_by_author(self, author):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_author, author)

        if self.debug_info:
            t_final = time.perf_counter()
            print("(INFO): {:.3f} s elapsed".format(t_final - t_init))

        return res

    # Query the DB by title
    def query_by_title(self, title):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_title, title)

        if self.debug_info:
            t_final = time.perf_counter()
            print("(INFO): {:.3f} s elapsed".format(t_final - t_init))

        return res

    # Query the DB by coordinates
    def query_by_coord(self, coord):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_coord, coord, self.numK)

        if self.debug_info:
            t_final = time.perf_counter()
            print("(INFO): {:.3f} s elapsed".format(t_final - t_init))

        return res

    ###### STATIC METHODS TO RUN CYPHER QUERIES ######

    # Insert a node in the DB given its properties
    @staticmethod
    def _insert_node(tx, pdf, author, title, coord):
        result = tx.run("MERGE (p:Paper {pdf:$pdf, author:$author, title:$title}) \
                        SET p.coord = $coord", \
                        pdf=pdf, author=author, title=title, coord=coord)

    # Create the GDS graph in the catalog using native projection
    @staticmethod
    def _create_gds_graph(tx, name):
        result = tx.run("CALL gds.graph.create($name, {Paper: {label: 'Paper', \
                        properties: 'coord'}}, '*') ", name=name)

    # Destroy GDS graph
    @staticmethod
    def _destroy_gds_graph(tx, name):
        result = tx.run("CALL gds.graph.drop($name, false) ", name=name)

    # Runs the KNN algo in the graph database based on cosine similarity
    @staticmethod
    def _run_knn(tx, name, K):
        result = tx.run("CALL gds.beta.knn.write($name,{writeRelationshipType: 'SIMILAR_TO', \
                        writeProperty: 'score', topK: $K, sampleRate: 1, deltaThreshold: 0, \
                        maxIterations: 1000, randomSeed: 0, nodeWeightProperty: 'coord'}) \
                        YIELD nodesCompared, relationshipsWritten ", name=name, K=K)

    # Query DB by author. Return matching papers and their nearest neighbours
    @staticmethod
    def _query_by_author(tx, author):
        result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.author \
                        = $author RETURN collect(DISTINCT p1) AS P1, collect(DISTINCT p2) \
                        AS P2 ", author=author)

        p1_list = []
        p2_list = []

        for r in result:
            for p1 in r["P1"]:
                prop = p1._properties
                p1_list.append({"id": p1._id, "pdf": prop["pdf"], "author": prop["author"], \
                                "title": prop["title"], "coord": prop["coord"]})
            for p2 in r["P2"]:
                prop = p2._properties
                p2_list.append({"id": p2._id, "pdf": prop["pdf"], "author": prop["author"], \
                                "title": prop["title"], "coord": prop["coord"]})

        return(p1_list, p2_list)

    # Query DB by paper title. Return matching papers and their nearest neighbours
    @staticmethod
    def _query_by_title(tx, title):
        result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.title \
                        = $title RETURN collect(DISTINCT p1) AS P1, collect(DISTINCT p2) \
                        AS P2 ", title=title)

        p1_list = []
        p2_list = []

        for r in result:
            for p1 in r["P1"]:
                prop = p1._properties
                p1_list.append({"id": p1._id, "pdf": prop["pdf"], "author": prop["author"], \
                                "title": prop["title"], "coord": prop["coord"]})
            for p2 in r["P2"]:
                prop = p2._properties
                p2_list.append({"id": p2._id, "pdf": prop["pdf"], "author": prop["author"], \
                                "title": prop["title"], "coord": prop["coord"]})

        return(p1_list, p2_list)

    # Query DB by coordinates. Return the nearest neighbours to the given coordinate
    @staticmethod
    def _query_by_coord(tx, coord, K):
        result = tx.run("MATCH (p:Paper) RETURN p, gds.alpha.similarity.cosine($coord, \
                        p.coord) AS sim ORDER BY sim DESC LIMIT $K ", coord=coord, K=K)

        p_list = []

        for r in result:
            p = r["p"]
            prop = p._properties
            p_list.append({"id": p._id, "pdf": prop["pdf"], "author": prop["author"], \
                            "title": prop["title"], "coord": prop["coord"]})

        return p_list

    # Remove all nodes and connections in the DB
    @staticmethod
    def _destroy_db(tx):
        result = tx.run("MATCH(p:Paper) DETACH DELETE p")

if __name__ == "__main__":
    # db_driver = DbDriver("bolt://localhost:7687", "neo4j", "capstone", 100, r"H:\Saad\University\Course Material\Fourth Year\Semester 2\ESC472\Project\NeuripsSplit\NeurIPS", True)
    # db_driver.build_db()
    # db_driver.build_knn_graph()
    # db_driver.close()
    init_db(r"H:\Saad\University\Course Material\Fourth Year\Semester 2\ESC472\Project\NeuripsSplit\NeurIPS")
