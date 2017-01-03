from config import *
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from time import ctime
import os

# Change working directory to the directory of this script so log files
# are created in this directory no matter where the script is run
os.chdir(os.path.dirname(os.path.abspath(__file__)))

graph_url = "https://graph.facebook.com/v2.8/"
images_directory = "static/images/"
page_id = page_info["page_id"]

def write_to_log(log_file, message):
    log_file.write("["+ctime()+"]:\t"+message+"\n")

def connect_to_database():
    options = {
        "host": db_info["host"],
        "user": db_info["user"],
        "passwd": db_info["password"],
        "db": db_info["db"],
        "cursorclass" : DictCursor
    }
    db = connect(**options)
    db.autocommit(True)
    return db
db = connect_to_database()

def execute_query(query, params=None):
    cursor = db.cursor()
    cursor.execute(query, params)
    query_results = cursor.fetchall()
    cursor.close()
    return query_results

def get_request_params(extra_params):
    params = {
        "access_token": page_info["access_token"]
    }
    params.update(extra_params)
    return params    
