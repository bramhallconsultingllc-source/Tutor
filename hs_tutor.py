export default function VVIDashboardMock() {
  const presentationMode = false;
  const TARGETS = {
    VVI: 2.0,
    RF: 1.0,
    LF: 1.0,
    REVENUE: 171,
    LABOR: 85,
  };

  const toPercent = (value) => `${Math.round(value * 100)}%`;
  const toVVIScore = (value) => Math.round((value / TARGETS.VVI) * 100);

  const vviLabel = (score) => {
    if (score >= 100) return "Excellent";
    if (score >= 85) return "Stable";
    if (score >= 70) return "At Risk";
    return "Critical";
  };

  const clinics = [
    { name: "Clinic A", vvi: 2.05, rf: 1.02, lf: 1.01, status: "Strong", issue: "None", revenue: 174, labor: 85, contribution: 89 },
    { name: "Clinic B", vvi: 1.62, rf: 0.92, lf: 0.85, status: "At Risk", issue: "Labor + Revenue", revenue: 157, labor: 97, contribution: 60 },
    { name: "Clinic C", vvi: 1.28, rf: 0.88, lf: 0.70, status: "Critical", issue: "Excess capacity", revenue: 150, labor: 117, contribution: 33 },
  ];

  const selected = clinics[1];
  const selectedScore = toVVIScore(selected.vvi);

  const statusBadge = (status) => {
    if (status === "Strong") return "bg-emerald-50 text-emerald-700";
    if (status === "At Risk") return "bg-orange-50 text-orange-600";
    return "bg-rose-50 text-rose-700";
  };

  const factorTone = (value) => {
    if (value >= 1.0) return "text-emerald-700";
    if (value >= 0.9) return "text-orange-600";
    return "text-rose-700";
  };

  const scoreTone = (score) => {
    if (score >= 100) return "text-emerald-700";
    if (score >= 85) return "text-orange-600";
    return "text-rose-700";
  };

  const rfActions = [
    {
      title: "Improve coding accuracy",
      detail: "Ensure appropriate E/M level selection and reduce undercoding.",
    },
    {
      title: "Strengthen POS collections",
      detail: "Increase upfront collections and reduce downstream leakage.",
    },
    {
      title: "Optimize payer mix",
      detail: "Target higher-acuity visits and commercial payers where possible.",
    },
  ];

  const lfActions = [
    {
      title: "Align staffing to demand",
      detail: "Reduce active rooms or adjust schedules to better match visit demand.",
    },
    {
      title: "Optimize provider productivity",
      detail: "Adjust provider templates and reduce idle capacity.",
    },
    {
      title: "Improve throughput",
      detail: "Reduce door-to-door time to increase visits per shift.",
    },
  ];

  return (
    <div className={presentationMode ? "min-h-screen bg-white p-4 md:p-6" : "min-h-screen bg-slate-50 p-6 md:p-10"}>
      <div className={presentationMode ? "max-w-[1400px] mx-auto space-y-4" : "max-w-7xl mx-auto space-y-6"}>
        <div className={presentationMode ? "bg-white p-5 rounded-3xl shadow-sm ring-1 ring-slate-200" : "bg-white p-6 rounded-3xl shadow-sm ring-1 ring-slate-200"}>
          <h2 className="text-xl font-semibold text-slate-900">Executive Summary</h2>
          <p className="mt-3 text-sm text-slate-600">
            VVI shows how much revenue each clinic generates for every dollar of labor.
          </p>
          <p className="mt-2 text-sm text-slate-600">
            This dashboard highlights performance gaps, identifies whether issues are driven by revenue or labor, and provides clear, prescriptive actions.
          </p>
          <p className="mt-2 text-sm text-slate-600">
            In this example, one clinic is performing strongly, one requires operational adjustment, and one requires immediate intervention.
          </p>
        </div>

        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-widest text-slate-500">Portfolio Dashboard</p>
            <h1 className="text-3xl font-semibold text-slate-900">Visit Value Index (VVI)</h1>
            <p className="mt-1 text-sm text-slate-500">
              Executive view of clinic performance, root-cause drivers, and prescriptive actions.
            </p>
          </div>

          <div className="bg-slate-900 text-white px-6 py-5 rounded-2xl shadow-lg min-w-56">
            <div className="text-xs uppercase tracking-widest text-slate-400">Portfolio Avg VVI</div>
            <div className="mt-2 text-4xl font-semibold">{toVVIScore(1.65)}</div>
            <div className="mt-1 text-sm text-orange-300">{vviLabel(toVVIScore(1.65))}</div>
          </div>
        </div>

        <div className={presentationMode ? "grid grid-cols-2 lg:grid-cols-4 gap-3" : "grid grid-cols-2 lg:grid-cols-4 gap-4"}>
          <div className="bg-white p-4 rounded-2xl shadow-sm ring-1 ring-slate-200">
            <div className="text-xs text-slate-500">Clinics</div>
            <div className="mt-2 text-2xl font-semibold text-slate-900">3</div>
          </div>
          <div className="bg-white p-4 rounded-2xl shadow-sm ring-1 ring-slate-200">
            <div className="text-xs text-slate-500">Strong</div>
            <div className="mt-2 text-2xl font-semibold text-emerald-700">1</div>
          </div>
          <div className="bg-white p-4 rounded-2xl shadow-sm ring-1 ring-slate-200">
            <div className="text-xs text-slate-500">At Risk</div>
            <div className="mt-2 text-2xl font-semibold text-orange-600">1</div>
          </div>
          <div className="bg-white p-4 rounded-2xl shadow-sm ring-1 ring-slate-200">
            <div className="text-xs text-slate-500">Critical</div>
            <div className="mt-2 text-2xl font-semibold text-rose-700">1</div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[1.35fr_0.95fr] gap-6">
          <div className="bg-white rounded-3xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-slate-900">Clinic comparison</h2>
                <p className="mt-1 text-xs text-slate-500">Quickly identify performance gaps across sites.</p>
              </div>
              <button className="bg-slate-900 text-white px-4 py-2 rounded-xl text-sm font-medium">Export</button>
            </div>

            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-6 py-3 text-left">Clinic</th>
                  <th className="px-6 py-3 text-left">VVI Score</th>
                  <th className="px-6 py-3 text-left">RF</th>
                  <th className="px-6 py-3 text-left">LF</th>
                  <th className="px-6 py-3 text-left">Status</th>
                  <th className="px-6 py-3 text-left">Key issue</th>
                </tr>
              </thead>
              <tbody>
                {clinics.map((c) => {
                  const score = toVVIScore(c.vvi);
                  const isSelected = c.name === selected.name;
                  return (
                    <tr key={c.name} className={`border-t border-slate-100 ${isSelected ? "bg-slate-100" : ""}`}>
                      <td className="px-6 py-4 font-medium text-slate-900">
                        {c.name}
                        {isSelected && <span className="ml-2 text-xs text-slate-400">Selected</span>}
                      </td>
                      <td className={`px-6 py-4 ${scoreTone(score)}`}>
                        <div className="font-semibold text-lg">{score}</div>
                        <div className="text-xs text-slate-400">{vviLabel(score)}</div>
                      </td>
                      <td className={`px-6 py-4 ${factorTone(c.rf)}`}>{toPercent(c.rf)}</td>
                      <td className={`px-6 py-4 ${factorTone(c.lf)}`}>{toPercent(c.lf)}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${statusBadge(c.status)}`}>
                          {c.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-600">{c.issue}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="space-y-6">
            <div className="bg-white p-6 rounded-3xl shadow-sm ring-1 ring-slate-200">
              <div className="flex justify-between items-start gap-4">
                <div>
                  <div className="text-xs uppercase tracking-widest text-slate-500">Selected clinic</div>
                  <h2 className="mt-1 text-2xl font-semibold text-slate-900">{selected.name}</h2>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${statusBadge(selected.status)}`}>
                  {selected.status}
                </span>
              </div>

              <div className="mt-6 bg-slate-900 text-white p-6 rounded-2xl">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-xs uppercase tracking-widest text-slate-400">VVI Score</div>
                    <div className="mt-2 text-5xl font-semibold">{selectedScore}</div>
                    <div className="mt-2 text-sm text-orange-300">{vviLabel(selectedScore)} vs target 100</div>
                  </div>
                  <div className="pt-2 text-right text-sm text-slate-300">
                    <div>Revenue per $1 labor</div>
                    <div className="mt-1 font-medium text-white">
                      {selected.vvi.toFixed(2)}x vs {TARGETS.VVI.toFixed(2)}x target
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-6">
                <div className="border border-slate-200 p-4 rounded-2xl">
                  <div className="text-xs uppercase tracking-widest text-slate-500">Revenue Factor</div>
                  <div className={`mt-2 text-2xl font-semibold ${factorTone(selected.rf)}`}>{toPercent(selected.rf)}</div>
                  <div className="mt-1 text-xs text-slate-400">Below target</div>
                </div>
                <div className="border border-slate-200 p-4 rounded-2xl">
                  <div className="text-xs uppercase tracking-widest text-slate-500">Labor Factor</div>
                  <div className={`mt-2 text-2xl font-semibold ${factorTone(selected.lf)}`}>{toPercent(selected.lf)}</div>
                  <div className="mt-1 text-xs text-slate-400">Below target</div>
                </div>
              </div>

              <div className="mt-6 bg-slate-50 p-4 rounded-2xl ring-1 ring-slate-200">
                <div className="text-xs uppercase tracking-widest text-slate-500">Diagnosis</div>
                <div className="mt-2 font-medium text-slate-800">Overstaffed relative to demand with moderate revenue capture gaps.</div>
                <div className="mt-2 text-sm text-slate-600">Labor cost per visit exceeds target due to excess capacity. Revenue capture is also below expected levels.</div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl shadow-sm ring-1 ring-slate-200">
              <h2 className="text-lg font-semibold text-slate-900">Prescriptive actions</h2>

              <div className="mt-4">
                <div className="text-sm font-semibold text-slate-700 mb-2">Revenue Actions (RF)</div>
                <div className="space-y-3">
                  {rfActions.map((action) => (
                    <div key={action.title} className="border border-slate-200 rounded-xl p-3">
                      <div className="font-medium text-slate-900">{action.title}</div>
                      <div className="text-sm text-slate-500">{action.detail}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <div className="text-sm font-semibold text-slate-700 mb-2">Labor Actions (LF)</div>
                <div className="space-y-3">
                  {lfActions.map((action) => (
                    <div key={action.title} className="border border-slate-200 rounded-xl p-3">
                      <div className="font-medium text-slate-900">{action.title}</div>
                      <div className="text-sm text-slate-500">{action.detail}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Unit Economics</h2>
            <p className="text-xs text-slate-500">Per-visit financial performance</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-2xl shadow-sm ring-1 ring-slate-200">
              <div className="text-xs uppercase tracking-widest text-slate-500">Net Revenue / Visit</div>
              <div className="mt-2 text-3xl font-semibold text-rose-600">$157</div>
              <div className="mt-1 text-xs text-slate-400">Target: $171</div>
            </div>
            <div className="bg-white p-4 rounded-2xl shadow-sm ring-1 ring-slate-200">
              <div className="text-xs uppercase tracking-widest text-slate-500">Labor Cost / Visit</div>
              <div className="mt-2 text-3xl font-semibold text-rose-600">$97</div>
              <div className="mt-1 text-xs text-slate-400">Target: $85</div>
            </div>
            <div className="bg-white p-4 rounded-2xl shadow-sm ring-1 ring-slate-200">
              <div className="text-xs uppercase tracking-widest text-slate-500">Contribution / Visit</div>
              <div className="mt-2 text-3xl font-semibold text-slate-900">$60</div>
              <div className="mt-1 text-xs text-slate-400">Revenue less labor</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
