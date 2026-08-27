const BASE_URL = "http://127.0.0.1:8000";

async function request(path) {
  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`);
  } catch {
    throw new Error("Can't reach the server — make sure the backend is running.");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export function searchPeople(query) {
  return request(`/api/people/search?q=${encodeURIComponent(query)}`);
}

export function getPersonProfile(personId) {
  return request(`/api/people/${encodeURIComponent(personId)}`);
}

export function getLineage(personId) {
  return request(`/api/people/${encodeURIComponent(personId)}/lineage`);
}

export function getSiblings(personId) {
  return request(`/api/people/${encodeURIComponent(personId)}/siblings`);
}

export function getCitationPath(paperA, paperB) {
  return request(
    `/api/citation-path?paper_a=${encodeURIComponent(paperA)}&paper_b=${encodeURIComponent(paperB)}`
  );
}