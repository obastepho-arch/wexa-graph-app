import { useState } from "react";
import { getCitationPath } from "../api";
import LineageMark from "./LineageMark";

export default function CitationPathFinder() {
  const [paperA, setPaperA] = useState("paper_5");
  const [paperB, setPaperB] = useState("paper_600");
  const [state, setState] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleFind(e) {
    e.preventDefault();
    setState("loading");
    setError("");
    try {
      const data = await getCitationPath(paperA.trim(), paperB.trim());
      setResult(data);
      setState("done");
    } catch (err) {
      setError(err.message);
      setState("error");
    }
  }

  return (
    <div className="panel">
      <form className="path-form" onSubmit={handleFind}>
        <label>
          Paper A id
          <input value={paperA} onChange={(e) => setPaperA(e.target.value)} placeholder="e.g. paper_5" />
        </label>
        <label>
          Paper B id
          <input value={paperB} onChange={(e) => setPaperB(e.target.value)} placeholder="e.g. paper_600" />
        </label>
        <button type="submit">Trace path</button>
      </form>

      {state === "loading" && (
        <p className="hint">
          <LineageMark size={14} spinning /> Walking the citation graph…
        </p>
      )}
      {state === "error" && (
        <p className="error">
          {error === "No citation path found within 10 hops"
            ? "No citation path connects these two papers within 10 hops. Try a different pair — see suggestions below."
            : error}
        </p>
      )}
      {state === "done" && result && (
        <div className="card">
          <h3>{result.hops}-hop path</h3>
          <ol className="path-chain">
            {result.path.map((node) => (
              <li key={node.id}>{node.title}</li>
            ))}
          </ol>
        </div>
      )}

      <p className="hint small">
        Try ids like paper_5, paper_50, paper_400, paper_600 — the seed data is
        randomly generated, so not every pair connects within 10 hops.
      </p>
    </div>
  );
}
