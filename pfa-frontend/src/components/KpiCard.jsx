import React from "react";

export default function KpiCard({ title, value, delta, icon }) {
  return (
    <div className="kpi-card">
      <div className="kpi-content">
        <div className="kpi-title">{title}</div>
        <div className="kpi-value">{value}</div>
        {delta && <div className="kpi-delta">{delta}</div>}
      </div>
      <div className="kpi-icon">{icon || "📊"}</div>
    </div>
  );
}
