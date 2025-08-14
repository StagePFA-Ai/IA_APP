import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function ChartBar({ data }) {
  return (
    <div className="chart-bar-container">
      <h3 className="chart-title">Réunions par jour</h3>
      <div className="chart-responsive-container">
        <ResponsiveContainer>
          <BarChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#5176c7" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
