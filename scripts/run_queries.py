"""
run_queries.py — runs the five core Cypher queries against your seeded
CognoDB data and prints the results, confirming the model actually works
end-to-end (not just that it's syntactically valid).
"""

import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USER = os.environ["COGNODB_USER"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def run(session, title, query, **params):
    print(f"\n=== {title} ===")
    records = list(session.run(query, **params))
    if not records:
        print("(no results — try a different person_/paper_ id, see note at bottom)")
        return
    for record in records[:15]:
        print(dict(record))
    if len(records) > 15:
        print(f"... and {len(records) - 15} more")


with driver.session() as session:

    run(
        session,
        "1. Full descendant lineage of person_5",
        """
        MATCH (root:Person {id: $personId})-[:ADVISED*1..6]->(descendant:Person)
        RETURN descendant.id AS id, descendant.name AS name
        """,
        personId="person_5",
    )

    run(
        session,
        "2. Longest ancestor chain above person_250",
        """
        MATCH path = (root:Person {id: $personId})<-[:ADVISED*1..6]-(ancestor:Person)
        RETURN [n IN nodes(path) | n.name] AS lineage
        ORDER BY length(path) DESC
        LIMIT 1
        """,
        personId="person_250",
    )

    run(
        session,
        "3. Shortest citation path between paper_5 and paper_600",
        """
        MATCH p = shortestPath(
          (a:Paper {id: $paperIdA})-[:CITES*..10]-(b:Paper {id: $paperIdB})
        )
        RETURN [n IN nodes(p) | n.title] AS path, length(p) AS hops
        """,
        paperIdA="paper_5",
        paperIdB="paper_600",
    )

    run(
        session,
        "4. Top 20 cross-institution citation influences",
        """
        MATCH (p1:Paper)<-[:AUTHORED]-(a1:Person)-[:AFFILIATED_WITH]->(i1:Institution),
              (p1)-[:CITES*1..4]->(p2:Paper)<-[:AUTHORED]-(a2:Person)-[:AFFILIATED_WITH]->(i2:Institution)
        WHERE i1 <> i2
        RETURN i1.name AS from_institution, i2.name AS to_institution, count(*) AS crossings
        ORDER BY crossings DESC
        LIMIT 20
        """,
    )

    run(
        session,
        "5. Academic siblings of person_250",
        """
        MATCH (advisor:Person)-[:ADVISED]->(p:Person {id: $personId}),
              (advisor)-[:ADVISED]->(sibling:Person)
        WHERE sibling.id <> $personId
        RETURN sibling.name
        """,
        personId="person_250",
    )

driver.close()
print(
    "\nDone. Queries 1, 2, 3, and 5 depend on the specific person_/paper_ id "
    "having the right kind of connection — since the seed data has randomness "
    "built in, an empty result there just means try a different id in that "
    "same range (e.g. person_10, person_180, paper_50, paper_400), not that "
    "something is broken. Query 4 (cross-institution) should reliably return "
    "rows regardless of which ids you use, since it isn't parameterized."
)
