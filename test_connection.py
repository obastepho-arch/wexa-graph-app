from dotenv import load_dotenv
load_dotenv()  # reads your .env file into the environment

import os
from neo4j import GraphDatabase

uri = os.environ["COGNODB_URI"]
user = os.environ["COGNODB_USER"]
password = os.environ["COGNODB_PASSWORD"]

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    result = session.run("RETURN 1 AS ok")
    print(result.single()["ok"])   # should print: 1

driver.close()