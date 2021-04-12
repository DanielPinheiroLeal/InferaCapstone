from neo4j import GraphDatabase
from pathlib import Path
import time
import numpy as np
import random
from model import *

class DbDriver:

    # Connect to the DB
    def __init__(self, uri, user, password, numK, numD, pdf_path, text_path, model_path, debug_info):

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.graph_name = 'neuripsGraph' # Name of the GDS graph
        self.numK = numK # Number of neighbours for the KNN algorithm
        self.numD = numD # Number of LSI dimensions
        self.pdf_path = pdf_path # FS path to the PDF files (It will search for PDFs recursively starting here)
        self.text_path = text_path # FS path to the .txt files
        self.model_path = model_path # FS path to the model
        self.debug_info = debug_info # Turn on/off debug messages
        self.ml_model = SimilarityModel(self.text_path, self.model_path, self.numD)

    # Close DB connection
    def close(self):
        self.driver.close()

    # Build the DB
    def build_db(self, train_model, create_db_nodes):
        if self.debug_info:
            t_init = time.perf_counter()

        print("\nBuilding model...\n")

        if train_model:
            print("\nWill train new model...\n")
        else:
            print("\nWill load existing model...\n")

        if train_model:
            #pdf_to_text(self.pdf_path, self.text_path)
            self.ml_model.build()
        else:
            self.ml_model.load()

        if create_db_nodes:
            print("\nBuilding database...\n")

            i = 0
            for path in Path(self.pdf_path).glob('*/*.pdf'):
                paper_id = i

                pdf = str(path)

                pdf_url = "http://localhost:8000/" + pdf.split(self.pdf_path,1)[1]

                author = "Jane Doe " + str(i) # Placeholder
                #print(path.stem)
                coord_tuple = self.ml_model.document_map(path.stem)
                title = path.stem.replace("_", " ")

                coord = [np.finfo(np.float64).eps] * self.numD
                for coordinate in coord_tuple[0]: # Get LSI coordinates
                    coord[coordinate[0]] = np.float64(coordinate[1])

                topic_prob = [0] * self.numD
                for coordinate in coord_tuple[1]: # Get LDA probabilities
                    topic_prob[coordinate[0]] = np.float64(coordinate[1])
                self.insert_node(paper_id, pdf, pdf_url, author, title, coord, topic_prob)
                i+=1

            print("\nDatabase successfully built! Number of papers: {}\n".format(i))

        if self.debug_info:
            t_final = time.perf_counter()
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
    def insert_node(self, paper_id, pdf, pdf_url, author, title, coord, topic_prob):
        with self.driver.session() as session:
            session.write_transaction(self._insert_node, paper_id, pdf, pdf_url, author, title, coord, topic_prob)

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

    # Query the DB by string
    def query_by_string(self, string):

        # Transform string into coordinate vector
        topic_coord = self.ml_model.string_lookup(string)
        string_coord = [0] * 10
        dim = 0
        for coord_tuple in topic_coord:
            string_coord[dim] = coord_tuple[1]
            dim+=1

        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_coord, string_coord, self.numK)

        if self.debug_info:
            t_final = time.perf_counter()
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return (res, t_tot)

        return res

    # Query the DB by model topic index
    def query_by_topic_index(self, topic_idx):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_topic_index, topic_idx, self.numK)

        if self.debug_info:
            t_final = time.perf_counter()
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return (res, t_tot)

        return res

    # Query the DB by paper_id. paper_id: int
    def query_by_paper_id(self, paper_id, mode):
        if self.debug_info:
            t_init = time.perf_counter()

        with self.driver.session() as session:
            res = session.read_transaction(self._query_by_paper_id, paper_id, self.numK, mode)

        if self.debug_info:
            t_final = time.perf_counter()
            t_tot = t_final-t_init
            print("(INFO): {:.3f} s elapsed".format(t_tot))
            return (res, t_tot)

        return res

    ###### STATIC METHODS TO RUN CYPHER QUERIES ######

    # Insert a node in the DB given its properties
    @staticmethod
    def _insert_node(tx, paper_id, pdf, pdf_url, author, title, coord, topic_prob):
        result = tx.run("MERGE (p:Paper {paper_id:$paper_id, pdf:$pdf, pdf_url:$pdf_url, author:$author, title:$title}) \
                        SET p.coord = $coord \
                        SET p.topic_prob = $topic_prob", \
                        paper_id=paper_id, pdf=pdf, pdf_url=pdf_url, author=author, title=title, coord=coord, topic_prob=topic_prob)

    # Create the GDS graph in the catalog using native projection
    @staticmethod
    def _create_gds_graph(tx, name):
        result = tx.run("CALL gds.graph.create($name, {Paper: {label: 'Paper', \
                        properties: { \
                            topic_prob: { \
                                property: 'topic_prob' \
                            }, \
                            coord: { \
                                property: 'coord' \
                            } \
                        }}}, '*') ", name=name)

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
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE toLower(p1.author) \
                        CONTAINS toLower($author) RETURN collect(DISTINCT p1) AS P ", author=author)
        elif mode == "related": # Return only related papers
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE toLower(p1.author) \
                        CONTAINS toLower($author) RETURN collect(DISTINCT p2) AS P ", author=author)
        else:
            print("Query mode not supported!")
            return

        p_list = []

        for r in result:
            for p in r["P"]:
                prop = p._properties
                p_list.append({"paper_id": prop["paper_id"], "pdf": prop["pdf"], "pdf_url": prop["pdf_url"], \
                                "author": prop["author"], "title": prop["title"], \
                                "coord": prop["coord"], "topic_prob": prop["topic_prob"]})

        return p_list

    # Query DB by paper title. Return matching papers and their nearest neighbours
    @staticmethod
    def _query_by_title(tx, title, mode):
        if mode == "exact": # Return only exact matches
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE toLower(p1.title) \
                        CONTAINS toLower($title) RETURN collect(DISTINCT p1) AS P ", title=title)
        elif mode == "related":
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE toLower(p1.title) \
                        CONTAINS toLower($title) RETURN collect(DISTINCT p2) AS P ", title=title)
        else:
            print("Query mode not supported!")
            return

        p_list = []

        for r in result:
            for p in r["P"]:
                prop = p._properties
                p_list.append({"paper_id": prop["paper_id"], "pdf": prop["pdf"], "pdf_url": prop["pdf_url"], \
                                "author": prop["author"], "title": prop["title"], \
                                "coord": prop["coord"], "topic_prob": prop["topic_prob"]})


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
            p_list.append({"paper_id": prop["paper_id"], "pdf": prop["pdf"], "pdf_url": prop["pdf_url"], \
                            "author": prop["author"], "title": prop["title"], \
                            "coord": prop["coord"], "topic_prob": prop["topic_prob"]})

        return p_list

    # Query DB by model topic index. Return the K papers that have highest probability
    # for the topic
    @staticmethod
    def _query_by_topic_index(tx, topic_idx, K):
        result = tx.run("MATCH (p:Paper) RETURN p, p.topic_prob[$topic_idx] AS prob \
                        ORDER BY prob DESC LIMIT $K ", topic_idx=topic_idx, K=K)

        p_list = []

        for r in result:
            p = r["p"]
            prop = p._properties
            p_list.append({"paper_id": prop["paper_id"], "pdf": prop["pdf"], "pdf_url": prop["pdf_url"], \
                            "author": prop["author"], "title": prop["title"], \
                            "coord": prop["coord"], "topic_prob": prop["topic_prob"]})

        return p_list

    # Query DB by paper id
    @staticmethod
    def _query_by_paper_id(tx, paper_id, K, mode):
        if mode == "exact": # Return only exact matches
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.paper_id \
                        = $paper_id RETURN collect(DISTINCT p1) AS P ", paper_id=paper_id)
        elif mode == "related":
            result = tx.run("MATCH (p1:Paper)-[s:SIMILAR_TO]->(p2:Paper) WHERE p1.paper_id \
                        = $paper_id RETURN collect(DISTINCT p2) AS P ", paper_id=paper_id)
        else:
            print("Query mode not supported!")
            return

        p_list = []

        for r in result:
            for p in r["P"]:
                prop = p._properties
                p_list.append({"paper_id": prop["paper_id"], "pdf": prop["pdf"], "pdf_url": prop["pdf_url"], \
                            "author": prop["author"], "title": prop["title"], \
                            "coord": prop["coord"], "topic_prob": prop["topic_prob"]})

        return p_list

    # Remove all nodes and connections in the DB
    @staticmethod
    def _destroy_db(tx):
        result = tx.run("MATCH(p:Paper) DETACH DELETE p")

if __name__ == "__main__":

    # Start DB driver
    db_driver = DbDriver("bolt://localhost:7687", "neo4j", "capstone", 100, 10, r"/bigdata/NeuripsArchive/NeurIPS/".rstrip(), r"/home/jeremy/Documents/UofT4/ESC472/InferaCapstone/NeurIPSText/".rstrip(), r"/home/jeremy/Documents/UofT4/ESC472/InferaCapstone/model/".rstrip(), False)

    # Destroy DB
    db_driver.destroy_db()

    # Build and populate DB
    db_driver.build_db(True, True)
    db_driver.build_knn_graph()
    test=db_driver.ml_model.document_map("Monotone_k-Submodular_Function_Maximization_with_Size_Constraints")
    print(test)
    # # Query DB by author name
    #p1_list = db_driver.query_by_author("Jane Doe " + str(0), "exact")
    #p2_list = db_driver.query_by_author("Jane Doe " + str(0), "related")
    #print(p1_list)
    #print(p2_list)

    # # Query DB by paper title
    # p1_list = db_driver.query_by_title("A_Computer_Simulation_of_Cerebral_Neocortex__Computational_Capabilities_of_Nonlinear_Neural_Networks", "exact")
    # p2_list = db_driver.query_by_title("A_Computer_Simulation_of_Olfactory_Cortex_with_Functional_Implications_for_Storage_and_Retrieval_of_Olfactory_Information", "related")
    # #print(p1_list)
    # #print(p2_list)

    # # Query DB by topic string
    # p_list = db_driver.query_by_string("Reinforcement learning")
    # #print(p_list)

    # # Query DB by model topic
    # model_topic_idx = 3
    # p_list = db_driver.query_by_topic_index(model_topic_idx)
    # #print(p_list)

    db_driver.close()

    # PERFORMANCE TESTS
    # -----------------

    # tear_down_times = [0] * 5
    # build_times = [0] * 5

    # for i in range(5):
    #     tear_down_times[i] = db_driver.destroy_db()

    #     build_db_t = db_driver.build_db()
    #     build_knn_t = db_driver.build_knn_graph()
    #     build_times[i] = build_db_t + build_knn_t

    # e_author_times = [0] * 1000
    # r_author_times = [0] * 1000

    # for i in range(1000):

    #     p1_list, e_author_times[i] = db_driver.query_by_author("Jane Doe " + str(i), "exact")
    #     p2_list, r_author_times[i] = db_driver.query_by_author("Jane Doe " + str(i), "related")

    # e_title_times = [0] * 1000
    # r_title_times = [0] * 1000

    # for i in range(1000):

    #     p1_list, e_title_times[i] = db_driver.query_by_title("Paper " + str(i), "exact")
    #     p2_list, r_title_times[i] = db_driver.query_by_title("Paper " + str(i), "related")


    # coord_times = [0] * 1000

    # for i in range(1000):

    #     p_list, coord_times[i] = db_driver.query_by_coord([random.random(), random.random(), random.random()])

    # connection_times = []

    # for i in range(100):
    #     connection_t1 = time.perf_counter()
    #     db_driver = DbDriver("bolt://localhost:7687", "neo4j", "capstone", 100, r"/bigdata/NeuripsArchive/NeurIPS/", True)
    #     connection_t2 = time.perf_counter()
    #     connection_times.append(connection_t2 - connection_t1)


    # print("\nTear Down Time: {:.5f} +- {:.5f} s\n".format(np.mean(tear_down_times), np.std(tear_down_times)))
    # print("\nBuild Time: {:.5f} +- {:.5f} s\n".format(np.mean(build_times), np.std(build_times)))
    # print("\nExact Author Time: {:.8f} +- {:.8f} s\n".format(np.mean(e_author_times), np.std(e_author_times)))
    # print("\nRelated Author Time: {:.8f} +- {:.8f} s\n".format(np.mean(r_author_times), np.std(r_author_times)))
    # print("\nExact Title Time: {:.8f} +- {:.8f} s\n".format(np.mean(e_title_times), np.std(e_title_times)))
    # print("\nRelated Title Time: {:.8f} +- {:.8f} s\n".format(np.mean(r_title_times), np.std(r_title_times)))
    # print("\nCoordinate Time: {:.8f} +- {:.8f} s\n".format(np.mean(coord_times), np.std(coord_times)))
    # print("\nConnection Time: {:.5f} +- {:.5f} s\n".format(np.mean(connection_times), np.std(connection_times)))
