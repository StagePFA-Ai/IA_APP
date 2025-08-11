import React from "react";

export default function KpiCard({ title, value, delta, icon }) {
  return (
    <div className="bg-white rounded shadow p-4 flex items-center justify-between">
      <div>
        <div className="text-sm text-gray-500">{title}</div>
        <div className="text-2xl font-bold">{value}</div>
        {delta && <div className="text-xs text-green-500 mt-1">{delta}</div>}
      </div>
      <div className="text-3xl text-gray-300">{icon || "📊"}</div>
    </div>
  );
}
