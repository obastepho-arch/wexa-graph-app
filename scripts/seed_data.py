"""
seed_data.py — populates CognoDB with realistic synthetic data for the
Academic Lineage & Citation Influence Explorer.

Safe to re-run: everything uses MERGE, so running this twice won't create
duplicates.
"""

import os
import random

from dotenv import load_dotenv
from faker import Faker
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USER = os.environ["COGNODB_USER"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

fake = Faker()
random.seed(42)  # reproducible data across runs

NUM_INSTITUTIONS = 25
NUM_PEOPLE = 300
NUM_PAPERS = 800

TOPICS = [
    "Machine Learning", "Databases", "Distributed Systems", "Computer Vision",
    "NLP", "Human-Computer Interaction", "Security", "Theory", "Robotics",
    "Bioinformatics", "Networks", "Graphics", "Programming Languages",
    "Systems", "Data Mining",
]
VENUES = ["NeurIPS", "ICML", "VLDB", "SIGMOD", "CHI", "CCS", "OSDI"]


def seed_institutions(tx):
    rows = [
        {"id": f"inst_{i}", "name": fake.company() + " University", "country": fake.country()}
        for i in range(NUM_INSTITUTIONS)
    ]
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (i:Institution {id: row.id})
        SET i.name = row.name, i.country = row.country
        """,
        rows=rows,
    )


def seed_topics(tx):
    rows = [{"id": f"topic_{i}", "name": name} for i, name in enumerate(TOPICS)]
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (t:Topic {id: row.id})
        SET t.name = row.name
        """,
        rows=rows,
    )


def seed_people(tx):
    rows = [
        {
            "id": f"person_{i}",
            "name": fake.name(),
            "stage": random.choice(
                ["PhD Student", "Postdoc", "Assistant Professor",
                 "Associate Professor", "Professor"]
            ),
            "year": random.randint(1985, 2022),
            "inst_id": f"inst_{random.randint(0, NUM_INSTITUTIONS - 1)}",
        }
        for i in range(NUM_PEOPLE)
    ]
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (p:Person {id: row.id})
        SET p.name = row.name, p.career_stage = row.stage, p.start_year = row.year
        WITH p, row
        MATCH (i:Institution {id: row.inst_id})
        MERGE (p)-[:AFFILIATED_WITH]->(i)
        """,
        rows=rows,
    )


def seed_advising(tx):
    rows = []
    for i in range(NUM_PEOPLE):
        if i > 20 and random.random() < 0.6:
            rows.append(
                {
                    "advisor": f"person_{random.randint(0, i - 1)}",
                    "advisee": f"person_{i}",
                    "year": random.randint(2000, 2023),
                }
            )
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (a:Person {id: row.advisor}), (p:Person {id: row.advisee})
        MERGE (a)-[:ADVISED {start_year: row.year}]->(p)
        """,
        rows=rows,
    )


def seed_papers(tx):
    rows = [
        {
            "id": f"paper_{i}",
            "title": fake.sentence(nb_words=6).rstrip("."),
            "year": random.randint(1995, 2024),
            "venue": random.choice(VENUES),
            "topic_id": f"topic_{random.randint(0, len(TOPICS) - 1)}",
        }
        for i in range(NUM_PAPERS)
    ]
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (pa:Paper {id: row.id})
        SET pa.title = row.title, pa.year = row.year, pa.venue = row.venue
        WITH pa, row
        MATCH (t:Topic {id: row.topic_id})
        MERGE (pa)-[:ABOUT]->(t)
        """,
        rows=rows,
    )


def seed_authorship(tx):
    rows = []
    for i in range(NUM_PAPERS):
        num_authors = random.randint(1, 4)
        for pid in random.sample(range(NUM_PEOPLE), num_authors):
            rows.append({"person_id": f"person_{pid}", "paper_id": f"paper_{i}"})
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (p:Person {id: row.person_id}), (pa:Paper {id: row.paper_id})
        MERGE (p)-[:AUTHORED]->(pa)
        """,
        rows=rows,
    )


def seed_citations(tx):
    """Preferential attachment: later papers cite earlier ones, weighted
    toward already-popular papers, mimicking real citation networks."""
    citation_counts = [1] * NUM_PAPERS
    rows = []
    for i in range(1, NUM_PAPERS):
        num_citations = random.randint(0, min(8, i))
        targets = set(
            random.choices(range(i), weights=citation_counts[:i], k=num_citations)
        )
        for t in targets:
            rows.append({"citing": f"paper_{i}", "cited": f"paper_{t}"})
            citation_counts[t] += 1
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (a:Paper {id: row.citing}), (b:Paper {id: row.cited})
        MERGE (a)-[:CITES]->(b)
        """,
        rows=rows,
    )


def main():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        print("Seeding institutions...")
        session.execute_write(seed_institutions)
        print("Seeding topics...")
        session.execute_write(seed_topics)
        print("Seeding people...")
        session.execute_write(seed_people)
        print("Seeding advising relationships...")
        session.execute_write(seed_advising)
        print("Seeding papers...")
        session.execute_write(seed_papers)
        print("Seeding authorship...")
        session.execute_write(seed_authorship)
        print("Seeding citations (preferential attachment)...")
        session.execute_write(seed_citations)
    driver.close()
    print("Done! Seed data loaded into CognoDB.")


if __name__ == "__main__":
    main()
