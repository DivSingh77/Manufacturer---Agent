"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Visualization = {
  type: "line" | "bar";
  title: string;
  x_key: string;
  y_key: string;
  data: Record<string, any>[];
};

type ApiResponse = {
  answer: string;
  persona: string;
  domain: string;
  intent: string;
  sql: string | null;
  data: {
    columns: string[];
    rows: any[][];
  };
  visualization: Visualization | null;
};

const EXAMPLES: Record<string, string[]> = {
  warehouse: [
    "Which items currently have zero stock?",
    "Show me the current stock by warehouse location.",
    "Show me recent inventory transactions.",
  ],

  procurement: [
    "Which purchase orders are partially received?",
    "Show details of PO-2026-0029 including vendor and items.",
    "Show receipts for PO-2026-0029.",
    "Show the purchase price history of MS C Channel – 125×65×5mm.",
  ],

  owner: [
    "What is the current stock of all items?",
    "Which vendors have the most purchase orders?",
    "Show details of PO-2026-0029 including vendor and items.",
  ],
};

export default function Home() {
  const [persona, setPersona] = useState("warehouse");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<ApiResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showSql, setShowSql] = useState(false);
  const [showTable, setShowTable] = useState(false);

  const isAccessDenied = useMemo(() => {
    return response?.answer
      ?.toLowerCase()
      .startsWith("access denied");
  }, [response]);

  async function handleSubmit(e?: React.FormEvent) {
    e?.preventDefault();

    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setResponse(null);
    setShowSql(false);
    setShowTable(false);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          persona,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      setResponse(data);
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  }

  function useExample(example: string) {
    setQuestion(example);
  }

  function renderVisualization() {
    if (!response?.visualization) {
      return null;
    }

    const viz = response.visualization;

    if (viz.type === "line") {
      return (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Visualization
            </p>

            <h2 className="mt-1 text-xl font-semibold text-slate-900">
              {viz.title}
            </h2>
          </div>

          <div className="h-[320px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={viz.data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={viz.x_key} />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey={viz.y_key}
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      );
    }

    if (viz.type === "bar") {
      return (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Visualization
            </p>

            <h2 className="mt-1 text-xl font-semibold text-slate-900">
              {viz.title}
            </h2>
          </div>

          <div className="h-[320px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={viz.data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={viz.x_key} />
                <YAxis />
                <Tooltip />
                <Bar dataKey={viz.y_key} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      );
    }

    return null;
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-7xl px-6 py-10">

        {/* Header */}

        <header className="mb-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">

            <div>
              <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">
                AI Operations Assistant
              </p>

              <h1 className="text-4xl font-bold tracking-tight text-slate-950">
                Manufacturer Agent
              </h1>

              <p className="mt-3 max-w-2xl text-slate-600">
                Persona-aware inventory and procurement intelligence powered
                by LangGraph, FastAPI and PostgreSQL.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm">
              <div className="text-slate-400">System status</div>
              <div className="mt-1 font-semibold text-emerald-600">
                ● Agent online
              </div>
            </div>

          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[330px_1fr]">

          {/* Sidebar */}

          <aside className="space-y-6">

            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

              <label className="text-sm font-semibold text-slate-800">
                Active persona
              </label>

              <select
                value={persona}
                onChange={(e) => {
                  setPersona(e.target.value);
                  setResponse(null);
                  setQuestion("");
                }}
                className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none focus:border-slate-500"
              >
                <option value="warehouse">Warehouse</option>
                <option value="procurement">Procurement</option>
                <option value="owner">Owner</option>
              </select>

              <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
                {persona === "warehouse" &&
                  "Inventory-only access. Procurement data is restricted."}

                {persona === "procurement" &&
                  "Procurement access with inventory item/location lookup only."}

                {persona === "owner" &&
                  "Cross-domain access to inventory and procurement data."}
              </div>

            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

              <h2 className="text-sm font-semibold text-slate-800">
                Example questions
              </h2>

              <div className="mt-4 space-y-2">
                {EXAMPLES[persona].map((example) => (
                  <button
                    key={example}
                    onClick={() => useExample(example)}
                    className="w-full rounded-xl border border-slate-200 px-4 py-3 text-left text-sm text-slate-600 transition hover:border-slate-400 hover:bg-slate-50"
                  >
                    {example}
                  </button>
                ))}
              </div>

            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-5 text-sm shadow-sm">

              <h2 className="font-semibold text-slate-800">
                Agent pipeline
              </h2>

              <div className="mt-4 space-y-2 text-slate-500">
                <div>1. Intent classification</div>
                <div>2. Persona access guard</div>
                <div>3. SQL generation</div>
                <div>4. SQL validation</div>
                <div>5. PostgreSQL execution</div>
                <div>6. Visualization</div>
                <div>7. Answer generation</div>
              </div>

            </section>

          </aside>

          {/* Main */}

          <div className="space-y-6">

            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

              <form onSubmit={handleSubmit}>

                <div className="mb-3 flex items-center justify-between">
                  <label className="text-sm font-semibold text-slate-800">
                    Ask the agent
                  </label>

                  <span className="text-xs uppercase tracking-wide text-slate-400">
                    {persona}
                  </span>
                </div>

                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask about inventory, purchase orders, vendors, receipts, pricing..."
                  rows={5}
                  className="w-full resize-none rounded-2xl border border-slate-300 bg-slate-50 p-4 text-slate-900 outline-none transition focus:border-slate-500 focus:bg-white"
                />

                <div className="mt-4 flex items-center justify-between">

                  <p className="text-xs text-slate-400">
                    Responses are generated from live PostgreSQL data.
                  </p>

                  <button
                    type="submit"
                    disabled={loading || !question.trim()}
                    className="rounded-xl bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {loading ? "Running agent..." : "Ask Agent"}
                  </button>

                </div>

              </form>

            </section>

            {loading && (
              <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="h-3 w-3 animate-pulse rounded-full bg-slate-900" />

                  <div>
                    <div className="font-medium text-slate-800">
                      Agent is processing your request
                    </div>

                    <div className="mt-1 text-sm text-slate-500">
                      Classifying, validating access and querying the database...
                    </div>
                  </div>
                </div>
              </section>
            )}

            {error && (
              <section className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700 shadow-sm">
                <h2 className="font-semibold">
                  Request failed
                </h2>

                <p className="mt-2 text-sm">
                  {error}
                </p>
              </section>
            )}

            {response && (
              <>

                {/* Metadata */}

                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600">
                    Persona: {response.persona}
                  </span>

                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600">
                    Domain: {response.domain}
                  </span>

                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600">
                    Intent: {response.intent}
                  </span>
                </div>

                {/* Answer */}

                <section
                  className={`rounded-2xl border p-6 shadow-sm ${
                    isAccessDenied
                      ? "border-amber-200 bg-amber-50"
                      : "border-slate-200 bg-white"
                  }`}
                >
                  <div className="mb-4">
                    <p
                      className={`text-xs font-semibold uppercase tracking-wider ${
                        isAccessDenied
                          ? "text-amber-600"
                          : "text-slate-400"
                      }`}
                    >
                      {isAccessDenied
                        ? "Access control"
                        : "Agent response"}
                    </p>

                    <h2 className="mt-1 text-xl font-semibold text-slate-900">
                      {isAccessDenied
                        ? "Request blocked"
                        : "Answer"}
                    </h2>
                  </div>

                  <div className="whitespace-pre-wrap leading-7 text-slate-700">
                    {response.answer}
                  </div>
                </section>

                {/* Visualization */}

                {renderVisualization()}

                {/* Technical details */}

                {(response.sql ||
                  response.data?.rows?.length > 0) && (
                  <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

                    <div className="flex flex-wrap gap-3">

                      {response.sql && (
                        <button
                          onClick={() => setShowSql(!showSql)}
                          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                        >
                          {showSql
                            ? "Hide SQL"
                            : "Show generated SQL"}
                        </button>
                      )}

                      {response.data?.rows?.length > 0 && (
                        <button
                          onClick={() =>
                            setShowTable(!showTable)
                          }
                          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                        >
                          {showTable
                            ? "Hide result table"
                            : `Show result table (${response.data.rows.length})`}
                        </button>
                      )}

                    </div>

                    {showSql && response.sql && (
                      <pre className="mt-5 max-h-[400px] overflow-auto rounded-xl bg-slate-950 p-5 text-sm leading-6 text-slate-100">
                        {response.sql}
                      </pre>
                    )}

                    {showTable &&
                      response.data?.rows?.length > 0 && (
                        <div className="mt-5 overflow-x-auto rounded-xl border border-slate-200">

                          <table className="min-w-full text-sm">

                            <thead className="bg-slate-50">
                              <tr>
                                {response.data.columns.map(
                                  (column) => (
                                    <th
                                      key={column}
                                      className="whitespace-nowrap border-b border-slate-200 px-4 py-3 text-left font-semibold text-slate-700"
                                    >
                                      {column}
                                    </th>
                                  )
                                )}
                              </tr>
                            </thead>

                            <tbody>
                              {response.data.rows
                                .slice(0, 50)
                                .map((row, rowIndex) => (
                                  <tr
                                    key={rowIndex}
                                    className="border-b border-slate-100 last:border-none"
                                  >
                                    {row.map(
                                      (cell, cellIndex) => (
                                        <td
                                          key={cellIndex}
                                          className="max-w-[320px] whitespace-nowrap px-4 py-3 text-slate-600"
                                        >
                                          {cell === null
                                            ? "—"
                                            : typeof cell ===
                                                "object"
                                            ? JSON.stringify(
                                                cell
                                              )
                                            : String(cell)}
                                        </td>
                                      )
                                    )}
                                  </tr>
                                ))}
                            </tbody>

                          </table>

                        </div>
                      )}

                    {showTable &&
                      response.data.rows.length > 50 && (
                        <p className="mt-3 text-xs text-slate-400">
                          Showing first 50 of{" "}
                          {response.data.rows.length} rows.
                        </p>
                      )}

                  </section>
                )}

              </>
            )}

          </div>

        </div>

      </div>
    </main>
  );
}