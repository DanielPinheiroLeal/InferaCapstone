'''
App backend database functions

Functions for server to interface with database via DbDriver
'''
import sys
from pathlib import Path

# add directory of db_driver.py to path for importing
db_driver_path = Path(__file__).resolve().parents[2] / "db_and_model"
sys.path.insert(1, str(db_driver_path))
from db_driver import DbDriver

def get_db(uri, user, password, num_neighbours, lsi_dims, lda_dims, pdf_path,
           text_path, model_path, debug_info, train_model, build_nodes,
           convert_pdfs):
    '''
    Connect to neo4j database and builds if desired

    Parameters:
        uri: [string] Database URI
        user: [string] Database account username
        password: [string] Database account password
        num_neighbours: [int] Number of connections for documents in graph database
        lsi_dims: [int] Number of dimensions for topic modelling (LSI)
        lda_dims: [int] Number of dimensions for topic modelling (LDA)
        pdf_path: [string] Path to top-level directory to recursively load PDF files from
        text_path: [string] Path to directory which stores all parsed PDF text files
        model_path: [string] Path to directory which stores saved model files
        debug_info: [bool] Whether to turn on or off debug info for database
        train_model: [bool] Whether to train new model or load existing
        build_nodes: [bool] Whether to create new database nodes or not
        convert_pdfs: [bool] Whether to convert PDFs to text files or load existing
    Returns:
        db: DbDriver instance
    '''
    print("[INFO]: Connecting to database")
    db = DbDriver(uri, user, password, num_neighbours, lsi_dims, lda_dims, pdf_path,
                  text_path, model_path, debug_info)

    # build the database with supplied arguments

    if build_nodes:
        db.destroy_db()

    db.build_db(train_model, build_nodes, convert_pdfs)

    if build_nodes:
        db.build_knn_graph()

    return db

def close_db(db):
    '''
    Close connection to database

    Parameters:
        db: DbDriver instance
    '''
    print("[INFO]: Closing connection to database")
    db.close()
