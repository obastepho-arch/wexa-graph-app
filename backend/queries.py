"""
queries.py — every Cypher query the app runs, as plain functions that take
a driver session and return plain Python data. Kept separate from main.py
so each query can be read and explained on its own.
"""


def search_people(session, name_query, limit=10):
    result = session.run(
        """
        MATCH (p:Person)
        WHERE toLower(p.name) CONTAINS toLower($q)
        RETURN p.id AS id, p.name AS name, p.career_stage AS careerStage
        LIMIT $limit
        """,
        q=name_query,
        limit=limit,
    )
    return [dict(r) for r in result]


def get_person_profile(session, person_id):
    result = session.run(
        """
        MATCH (p:Person {id: $id})
        OPTIONAL MATCH (advisor:Person)-[:ADVISED]->(p)
        OPTIONAL MATCH (p)-[:ADVISED]->(advisee:Person)
        OPTIONAL MATCH (p)-[:AUTHORED]->(paper:Paper)
        OPTIONAL MATCH (p)-[:AFFILIATED_WITH]->(inst:Institution)
        RETURN p.id AS id, p.name AS name, p.career_stage AS careerStage,
               inst.name AS institution,
               collect(DISTINCT advisor.name) AS advisors,
               collect(DISTINCT advisee.name) AS advisees,
               collect(DISTINCT {id: paper.id, title: paper.title, year: paper.year}) AS papers
        """,
        id=person_id,
    )
    record = result.single()
    return dict(record) if record else None


def get_lineage(session, person_id):
    result = session.run(
        """
        MATCH (root:Person {id: $id})-[:ADVISED*1..6]->(descendant:Person)
        RETURN descendant.id AS id, descendant.name AS name
        """,
        id=person_id,
    )
    return [dict(r) for r in result]


def get_shortest_citation_path(session, paper_id_a, paper_id_b):
    result = session.run(
        """
        MATCH p = shortestPath(
          (a:Paper {id: $a})-[:CITES*..10]-(b:Paper {id: $b})
        )
        RETURN [n IN nodes(p) | {id: n.id, title: n.title}] AS path, length(p) AS hops
        """,
        a=paper_id_a,
        b=paper_id_b,
    )
    record = result.single()
    return dict(record) if record else None


def get_cross_institution_stats(session, limit=20):
    result = session.run(
        """
        MATCH (p1:Paper)<-[:AUTHORED]-(a1:Person)-[:AFFILIATED_WITH]->(i1:Institution),
              (p1)-[:CITES*1..4]->(p2:Paper)<-[:AUTHORED]-(a2:Person)-[:AFFILIATED_WITH]->(i2:Institution)
        WHERE i1 <> i2
        RETURN i1.name AS fromInstitution, i2.name AS toInstitution, count(*) AS crossings
        ORDER BY crossings DESC
        LIMIT $limit
        """,
        limit=limit,
    )
    return [dict(r) for r in result]


def get_siblings(session, person_id):
    result = session.run(
        """
        MATCH (advisor:Person)-[:ADVISED]->(p:Person {id: $id}),
              (advisor)-[:ADVISED]->(sibling:Person)
        WHERE sibling.id <> $id
        RETURN sibling.id AS id, sibling.name AS name
        """,
        id=person_id,
    )
    return [dict(r) for r in result]
