"""
db.py — owns the single CognoDB driver connection for the whole app.
"""

import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USER = os.environ["COGNODB_USER"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_session():
    return driver.session()


def close_driver():
    driver.close()
