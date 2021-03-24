from neo4j import GraphDatabase
from pathlib import Path
import time
import numpy as np

import random

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
            i+=1

        if self.debug_info:
            t_final = time.perf_counter()

        print("\nDatabase successfully built! Number of papers: {}\n".format(i))

        if self.debug_info:
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return t_tot

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
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return t_tot

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
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return t_tot

    # Query the DB by author
    # mode: 'exact' - get exact matches; 'related' - get related results
    def query_by_author(self, author, mode):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_author, author, mode)

        if self.debug_info:
            t_final = time.perf_counter()
            t_tot = t_final-t_init
            print("\n(INFO): {:.3f} s elapsed".format(t_tot))
            return (res, t_tot)

        return res

    # Query the DB by title
    # mode: 'exact' - get exact matches; 'related' - get related results
    def query_by_title(self, title, mode):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_title, title, mode)

        if self.debug_info:
            t_final = time.perf_counter()
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return (res, t_tot)

        return res

    # Query the DB by coordinates
    def query_by_coord(self, coord):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_coord, coord, self.numK)

        if self.debug_info:
            t_final = time.perf_counter()
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return (res, t_tot)

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
    def _query_by_author(tx, author, mode):
        if mode == "exact": # Return only exact matches
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.author \
                        = $author RETURN collect(DISTINCT p1) AS P ", author=author)
        elif mode == "related": # Return only related papers
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.author \
                        = $author RETURN collect(DISTINCT p2) AS P ", author=author)
        else:
            print("Query mode not supported!")
            return

        p_list = []

        for r in result:
            for p in r["P"]:
                prop = p._properties
                p_list.append({"id": p._id, "pdf": prop["pdf"], "author": prop["author"], \
                                "title": prop["title"], "coord": prop["coord"]})

        return p_list

    # Query DB by paper title. Return matching papers and their nearest neighbours
    @staticmethod
    def _query_by_title(tx, title, mode):
        if mode == "exact": # Return only exact matches
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.title \
                        = $title RETURN collect(DISTINCT p1) AS P ", title=title)
        elif mode == "related":
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.title \
                        = $title RETURN collect(DISTINCT p2) AS P ", title=title)
        else:
            print("Query mode not supported!")
            return

        p_list = []

        for r in result:
            for p in r["P"]:
                prop = p._properties
                p_list.append({"id": p._id, "pdf": prop["pdf"], "author": prop["author"], \
                                "title": prop["title"], "coord": prop["coord"]})


        return p_list

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

    db_driver = DbDriver("bolt://localhost:7687", "neo4j", "capstone", 100, r"/bigdata/NeuripsArchive/NeurIPS/", True)

    tear_down_times = [0] * 5
    build_times = [0] * 5

    for i in range(5):
        tear_down_times[i] = db_driver.destroy_db()

        build_db_t = db_driver.build_db()
        build_knn_t = db_driver.build_knn_graph()
        build_times[i] = build_db_t + build_knn_t

    e_author_times = [0] * 1000
    r_author_times = [0] * 1000

    for i in range(1000):

        p1_list, e_author_times[i] = db_driver.query_by_author("Jane Doe " + str(i), "exact")
        p2_list, r_author_times[i] = db_driver.query_by_author("Jane Doe " + str(i), "related")

    e_title_times = [0] * 1000
    r_title_times = [0] * 1000

    for i in range(1000):

        p1_list, e_title_times[i] = db_driver.query_by_title("Paper " + str(i), "exact")
        p2_list, r_title_times[i] = db_driver.query_by_title("Paper " + str(i), "related")


    coord_times = [0] * 1000

    for i in range(1000):

        p_list, coord_times[i] = db_driver.query_by_coord([random.random(), random.random(), random.random()])

    connection_times = []

    for i in range(100):
        connection_t1 = time.perf_counter()
        db_driver = DbDriver("bolt://localhost:7687", "neo4j", "capstone", 100, r"/bigdata/NeuripsArchive/NeurIPS/", True)
        connection_t2 = time.perf_counter()
        connection_times.append(connection_t2 - connection_t1)


    print("\nTear Down Time: {:.5f} +- {:.5f} s\n".format(np.mean(tear_down_times), np.std(tear_down_times)))
    print("\nBuild Time: {:.5f} +- {:.5f} s\n".format(np.mean(build_times), np.std(build_times)))
    print("\nExact Author Time: {:.8f} +- {:.8f} s\n".format(np.mean(e_author_times), np.std(e_author_times)))
    print("\nRelated Author Time: {:.8f} +- {:.8f} s\n".format(np.mean(r_author_times), np.std(r_author_times)))
    print("\nExact Title Time: {:.8f} +- {:.8f} s\n".format(np.mean(e_title_times), np.std(e_title_times)))
    print("\nRelated Title Time: {:.8f} +- {:.8f} s\n".format(np.mean(r_title_times), np.std(r_title_times)))
    print("\nCoordinate Time: {:.8f} +- {:.8f} s\n".format(np.mean(coord_times), np.std(coord_times)))
    print("\nConnection Time: {:.5f} +- {:.5f} s\n".format(np.mean(connection_times), np.std(connection_times)))

    #db_driver.destroy_db()

    db_driver.close()
