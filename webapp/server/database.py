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

db_account = {
    "user": "neo4j",
    "password": "capstone"
}

def get_db(uri="bolt://localhost:7687", user=db_account["user"],
           password=db_account["password"], num_neighbours=25, lsi_dims=10,
           pdf_path="/bigdata/NeuripsArchive/NeurIPS/", text_path="/home/jeremy/Documents/UofT4/ESC472/InferaCapstone/NeurIPSText/", model_path="/home/jeremy/Documents/UofT4/ESC472/model/", debug_info=False):
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
    db = DbDriver(uri, user, password, num_neighbours, lsi_dims, pdf_path,
                  text_path, model_path, debug_info)
    db.build_db(False,False)
    return db

def close_db(db):
    '''
    Close connection to database

    Parameters:
        db: DbDriver instance
    '''
    print("[INFO]: Closing connection to database")
    db.close()
