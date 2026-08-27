import { useState } from "react";
import { searchPeople, getPersonProfile, getLineage, getSiblings } from "../api";
import LineageMark from "./LineageMark";

export default function ResearcherExplorer() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searchState, setSearchState] = useState("idle"); // idle | loading | error | done
  const [selected, setSelected] = useState(null);
  const [profile, setProfile] = useState(null);
  const [lineage, setLineage] = useState([]);
  const [siblings, setSiblings] = useState([]);
  const [detailState, setDetailState] = useState("idle");
  const [error, setError] = useState("");

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setSearchState("loading");
    setError("");
    try {
      const data = await searchPeople(query.trim());
      setResults(data);
      setSearchState("done");
    } catch (err) {
      setError(err.message);
      setSearchState("error");
    }
  }

  async function handleSelect(person) {
    setSelected(person);
    setDetailState("loading");
    setError("");
    try {
      const [profileData, lineageData, siblingsData] = await Promise.all([
        getPersonProfile(person.id),
        getLineage(person.id),
        getSiblings(person.id),
      ]);
      setProfile(profileData);
      setLineage(lineageData);
      setSiblings(siblingsData);
      setDetailState("done");
    } catch (err) {
      setError(err.message);
      setDetailState("error");
    }
  }

  return (
    <div className="panel">
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search a researcher by name…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      {searchState === "loading" && (
        <p className="hint">
          <LineageMark size={14} spinning /> Searching the record…
        </p>
      )}
      {searchState === "error" && <p className="error">{error}</p>}
      {searchState === "done" && results.length === 0 && (
        <p className="hint">
          No record found for "{query}" — try a different spelling or just a surname.
        </p>
      )}

      <div className="layout-two-col">
        <ul className="result-list">
          {results.map((p) => (
            <li key={p.id}>
              <button
                className={selected?.id === p.id ? "selected" : ""}
                onClick={() => handleSelect(p)}
              >
                {p.name} <span className="muted">— {p.careerStage}</span>
              </button>
            </li>
          ))}
        </ul>

        <div className="detail-pane">
          {!selected && (
            <p className="hint">Select a name from the index to open their record.</p>
          )}
          {detailState === "loading" && (
            <p className="hint">
              <LineageMark size={14} spinning /> Pulling the record…
            </p>
          )}
          {detailState === "error" && <p className="error">{error}</p>}
          {detailState === "done" && profile && (
            <div className="card">
              <h2>{profile.name}</h2>
              <span className="muted">
                {profile.careerStage} · {profile.institution || "Unaffiliated"}
              </span>

              <h3>Advisor</h3>
              <p>
                {profile.advisors?.filter(Boolean).length
                  ? profile.advisors.filter(Boolean).join(", ")
                  : "None on record"}
              </p>

              <h3>Advisees</h3>
              <p>
                {profile.advisees?.filter(Boolean).length
                  ? profile.advisees.filter(Boolean).join(", ")
                  : "None on record"}
              </p>

              <h3>Papers</h3>
              {profile.papers?.filter((p) => p.id).length ? (
                <ul>
                  {profile.papers
                    .filter((p) => p.id)
                    .map((p) => (
                      <li key={p.id}>
                        {p.title} <span className="muted">({p.year})</span>
                      </li>
                    ))}
                </ul>
              ) : (
                <p className="muted">No papers on record</p>
              )}

              <h3>Full descendant lineage ({lineage.length})</h3>
              {lineage.length ? (
                <ul>
                  {lineage.map((d) => (
                    <li key={d.id}>{d.name}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No academic descendants on record</p>
              )}

              <h3>Academic siblings ({siblings.length})</h3>
              {siblings.length ? (
                <ul>
                  {siblings.map((s) => (
                    <li key={s.id}>{s.name}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No shared advisor found</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
