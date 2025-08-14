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
     <div className="dashboard">
      <div className="kpi-grid">
        {kpis.map((k,i) => <KpiCard key={i} {...k} />)}
      </div>

      <div className="content-grid">
        <div className="main-column">
          <ChartBar data={barData} />
          <ChartLine data={lineData} />
        </div>
        <div className="side-column">
          <div className="card">
            <h3 className="section-title">Actions Rapides</h3>
            <button className="btn btn-primary">Rapport mensuel</button>
            <button className="btn btn-secondary">Exporter</button>
          </div>
          <div className="card">
            <h3 className="section-title">Activité</h3>
            <ul className="activity-list">
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
