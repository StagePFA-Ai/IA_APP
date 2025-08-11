import React, { useEffect, useState } from "react";
import KpiCard from "../components/KpiCard";
import ChartBar from "../components/ChartBar";
import ChartLine from "../components/ChartLine";
import { fetchMeetings } from "../services/api";

export default function Dashboard() {
  const [meetings, setMeetings] = useState([]);

  useEffect(() => { load(); }, []);

  async function load() {
    try {
      const data = await fetchMeetings();
      setMeetings(data || []);
    } catch (err) {
      setMeetings([]);
    }
  }

  const kpis = [
    { title: "Réunions", value: meetings.length, delta: "+12%"},
    { title: "Heures", value: Math.round((meetings.reduce((a,m)=>a + (m.duration||0),0))/60) || 0, delta: "+8%"},
    { title: "Résumés", value: meetings.filter(m=>m.summary).length, delta: "+15%"},
    { title: "Actions", value: meetings.filter(m=>m.status === 'pending').length, delta: "-5%"}
  ];

  const barData = [ {name:'Lun',value:4},{name:'Mar',value:6},{name:'Mer',value:3},{name:'Jeu',value:8},{name:'Ven',value:5},{name:'Sam',value:1} ];
  const lineData = [ {name:'S1',value:200},{name:'S2',value:450},{name:'S3',value:320} ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {kpis.map((k,i) => <KpiCard key={i} {...k} />)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <ChartBar data={barData} />
          <ChartLine data={lineData} />
        </div>
        <div className="space-y-4">
          <div className="bg-white p-4 rounded shadow">
            <h3 className="font-semibold mb-2">Actions Rapides</h3>
            <button className="bg-blue-50 text-blue-700 px-3 py-1 rounded mr-2">Rapport mensuel</button>
            <button className="bg-gray-50 px-3 py-1 rounded">Exporter</button>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <h3 className="font-semibold mb-2">Activité</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>Enregistrement automatique activé</li>
              <li>Notes partagées</li>
              <li>Actions en attente: 3</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
