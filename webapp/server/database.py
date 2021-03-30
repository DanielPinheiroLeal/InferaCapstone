'''
App backend database functions
'''
import sys
from pathlib import Path

# add directory of db_driver.py to path for importing
db_driver_path = Path(__file__).resolve().parents[2] / "db_and_model"
sys.path.insert(1, str(db_driver_path))
from db_driver import DbDriver

db_account = {
    "user": "neo4j",
    "password": "capstone"
}

def get_db(pdf_path="", uri="bolt://localhost:7687", user=db_account["user"], 
           password=db_account["password"], num_neighbours=25, debug_info=False):
    '''
    Connect to neo4j database

    Parameters:
        pdf_path: [string] Top-level path to recursively load PDF files from to populate database
        uri: [string] Database URI
        user: [string] Database account username
        password: [string] Database account password
        num_neighbours: [int] Number of nearest neighbours to compute between points in graph database
        debug_info: [bool] Whether to turn on or off debug info for database
    Returns:
        db: DbDriver instance
    '''
    print("[INFO]: Connecting to database")
    db = DbDriver(uri, user, password, num_neighbours, pdf_path, debug_info)
    return db

def close_db(db):
    '''
    Close connection to database

    Parameters:
        db: DbDriver instance
    '''
    print("[INFO]: Closing connection to database")
    db.close()

def init_db(pdf_path, uri="bolt://localhost:7687", user=db_account["user"], 
            password=db_account["password"], num_neighbours=25, debug_info=False):
    '''
    Populate database with PDFs and build kNN graph

    Parameters:
        pdf_path: [string] Top-level path to recursively load PDF files from to populate database
        uri: [string] Database URI
        user: [string] Database account username
        password: [string] Database account password
        num_neighbours: [int] Number of nearest neighbours to compute between points in graph database
        debug_info: [bool] Whether to turn on or off debug info for database
    '''
    print("[INFO]: Initializing database")
    db = get_db(pdf_path=pdf_path, num_neighbours=num_neighbours)
    db.build_db()
    db.build_knn_graph()
