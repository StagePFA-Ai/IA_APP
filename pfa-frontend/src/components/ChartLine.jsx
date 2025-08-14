import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function ChartLine({ data }) {
  return (
    <div className="chart-line-container">
      <h3 className="chart-line-title">Durée totale (minutes)</h3>
      <div className="chart-line-responsive-container">
        <ResponsiveContainer className="chart-line">
          <LineChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#41b991" 
              strokeWidth={2} 
              dot={{ fill: '#41b991', strokeWidth: 2, r: 4 }}
              activeDot={{ fill: '#2f855a', strokeWidth: 0, r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
