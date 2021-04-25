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

db_uri = "bolt://localhost:7687"
db_account = {
    "user": "neo4j",
    "password": "capstone"
}

def get_db(uri=db_uri, user=db_account["user"],
           password=db_account["password"], num_neighbours=25, lsi_dims=10, lda_dims=10,
           pdf_path="", text_path="", model_path="", debug_info=False, build_nodes = True, train_model = True,
           convert_pdfs = True):
    '''
    Connect to neo4j database

    Parameters:
        uri: [string] Database URI
        user: [string] Database account username
        password: [string] Database account password
        num_neighbours: [int] Number of nearest neighbours to compute between points in graph database
        lsi_dims: [int] Number of dimensions for latent semantic indexing
        pdf_path: [string] Path to top-level directory to recursively load PDF files from
        text_path: [string] Path to directory which stores all parsed PDF text files
        model_path: [string] Path to directory which stores saved model files
        debug_info: [bool] Whether to turn on or off debug info for database
    Returns:
        db: DbDriver instance
    '''
    print("[INFO]: Connecting to database")
    db = DbDriver(uri, user, password, num_neighbours, lsi_dims, lda_dims, pdf_path,
                  text_path, model_path, debug_info)
    
    if build_nodes:
        db.destroy_db()
    
    #build the database with supplied arguments
    print(convert_pdfs)
    db.build_db(train_model, build_nodes, convert_pdfs)
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
