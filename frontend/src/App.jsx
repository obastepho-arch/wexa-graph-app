import { useState } from "react";
import ResearcherExplorer from "./components/ResearcherExplorer";
import CitationPathFinder from "./components/CitationPathFinder";
import LineageMark from "./components/LineageMark";
import "./App.css";

export default function App() {
  const [tab, setTab] = useState("explorer");

  return (
    <div className="app">
      <header className="masthead">
        <LineageMark size={30} />
        <div>
          <h1>Academic Lineage &amp; Citation Influence</h1>
          <div className="subtitle">An explorer of advising trees &amp; citation trails</div>
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === "explorer" ? "active" : ""} onClick={() => setTab("explorer")}>
          Researcher Index
        </button>
        <button className={tab === "path" ? "active" : ""} onClick={() => setTab("path")}>
          Citation Path Finder
        </button>
      </nav>

      <main>{tab === "explorer" ? <ResearcherExplorer /> : <CitationPathFinder />}</main>
    </div>
  );
}
