
import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/reconciliation/";

function App() {
  const [org, setOrg] = useState("ORG-A");
  const [reason, setReason] = useState("ALL");
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [ascending, setAscending] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchReconciliation() {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(
          `${API_URL}?org=${encodeURIComponent(org)}`,
          { signal: controller.signal }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to load reconciliation data");
        }

        setResults(data.results || []);
        setTotal(data.total_disagreements || 0);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message || "Unable to connect to backend");
          setResults([]);
          setTotal(0);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchReconciliation();

    return () => controller.abort();
  }, [org]);

  const filteredResults = useMemo(() => {
    let data = [...results];

    if (reason !== "ALL") {
      data = data.filter((item) => item.reason === reason);
    }

    data.sort((a, b) => {
      const valueA = Number(a.a_value ?? 0);
      const valueB = Number(b.a_value ?? 0);

      return ascending ? valueA - valueB : valueB - valueA;
    });

    return data;
  }, [results, reason, ascending]);

  const formatValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "—";
    }

    const number = Number(value);

    return Number.isNaN(number)
      ? value
      : number.toLocaleString("en-IN", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });
  };

  const reasonLabel = (value) =>
    String(value || "").replaceAll("_", " ");

  const uniqueReasons = [...new Set(results.map((item) => item.reason))];

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>DealerOS</h1>
          <p>Financial Reconciliation Dashboard</p>
        </div>

        <div className="header-tag">CSV RECONCILIATION</div>
      </header>

      <main className="container">
        <section className="welcome">
          <div>
            <h2>Reconciliation Overview</h2>
            <p>
              Compare System A and System B records and identify
              discrepancies across organizations.
            </p>
          </div>
        </section>

        <section className="summary-grid">
          <div className="summary-card">
            <span className="summary-label">Organization</span>
            <strong>{org}</strong>
            <span className="summary-description">Selected organization</span>
          </div>

          <div className="summary-card">
            <span className="summary-label">Total Disagreements</span>
            <strong>{total}</strong>
            <span className="summary-description">Detected records</span>
          </div>

          <div className="summary-card">
            <span className="summary-label">Filtered Results</span>
            <strong>{filteredResults.length}</strong>
            <span className="summary-description">Currently displayed</span>
          </div>
        </section>

        <section className="table-section">
          <div className="section-heading">
            <div>
              <h2>Disagreement Records</h2>
              <p>Review and investigate mismatched transactions.</p>
            </div>
          </div>

          <div className="filters">
            <div className="filter-group">
              <label htmlFor="organization">Organization</label>
              <select
                id="organization"
                value={org}
                onChange={(e) => {
                  setOrg(e.target.value);
                  setReason("ALL");
                }}
              >
                <option value="ORG-A">ORG-A</option>
                <option value="ORG-B">ORG-B</option>
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="reason">Filter by Reason</label>
              <select
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              >
                <option value="ALL">All Reasons</option>
                {uniqueReasons.map((item) => (
                  <option key={item} value={item}>
                    {reasonLabel(item)}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="sort-button"
              onClick={() => setAscending((previous) => !previous)}
            >
              Sort by System A Value {ascending ? "↑" : "↓"}
            </button>
          </div>

          {loading && <div className="message">Loading reconciliation data...</div>}

          {error && (
            <div className="error-message">
              <strong>Unable to load data.</strong>
              <p>{error}</p>
              <span>
                Make sure the Django backend is running on port 8000.
              </span>
            </div>
          )}

          {!loading && !error && (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Reason</th>
                    <th>Record ID</th>
                    <th>Location</th>
                    <th>System A Value</th>
                    <th>System B Value</th>
                    <th>Difference</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredResults.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="empty">
                        No disagreement records found.
                      </td>
                    </tr>
                  ) : (
                    filteredResults.map((item, index) => (
                      <tr key={`${item.record_id}-${item.reason}-${index}`}>
                        <td>
                          <span className="reason-badge">
                            {reasonLabel(item.reason)}
                          </span>
                        </td>
                        <td className="record-id">{item.record_id || "—"}</td>
                        <td>{item.location || "—"}</td>
                        <td className="amount">
                          {formatValue(item.a_value)}
                        </td>
                        <td className="amount">
                          {formatValue(item.b_value)}
                        </td>
                        <td className="amount difference">
                          {formatValue(item.difference)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <footer>
          DealerOS Reconciliation System · Data sourced from imported CSV files
        </footer>
      </main>
    </div>
  );
}

export default App;
