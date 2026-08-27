"""
main.py — the FastAPI app itself. Each route calls one function from
queries.py and turns database errors into clean HTTP responses instead of
crashing.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j.exceptions import AuthError, ServiceUnavailable

import queries
from db import close_driver, get_session

app = FastAPI(title="Academic Lineage & Citation Influence API")

# Allows your React dev server (usually on port 5173) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
def shutdown():
    close_driver()


def run_query(query_fn, *args, **kwargs):
    """Wraps every query call so a database outage becomes a clean 503,
    not a crash with a raw stack trace."""
    try:
        with get_session() as session:
            return query_fn(session, *args, **kwargs)
    except (ServiceUnavailable, AuthError) as exc:
        raise HTTPException(
            status_code=503,
            detail="The database is unreachable right now. Please try again shortly.",
        ) from exc


@app.get("/")
def root():
    return {"status": "ok", "message": "Academic Lineage API is running"}


@app.get("/api/people/search")
def search_people(q: str = Query(..., min_length=1)):
    return run_query(queries.search_people, q)


@app.get("/api/people/{person_id}")
def person_profile(person_id: str):
    result = run_query(queries.get_person_profile, person_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return result


@app.get("/api/people/{person_id}/lineage")
def person_lineage(person_id: str):
    return run_query(queries.get_lineage, person_id)


@app.get("/api/people/{person_id}/siblings")
def person_siblings(person_id: str):
    return run_query(queries.get_siblings, person_id)


@app.get("/api/citation-path")
def citation_path(paper_a: str, paper_b: str):
    result = run_query(queries.get_shortest_citation_path, paper_a, paper_b)
    if result is None:
        raise HTTPException(
            status_code=404, detail="No citation path found within 10 hops"
        )
    return result


@app.get("/api/cross-institution")
def cross_institution():
    return run_query(queries.get_cross_institution_stats)
