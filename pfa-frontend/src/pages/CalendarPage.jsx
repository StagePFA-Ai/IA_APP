import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import { fetchMeetings } from "../services/api";

export default function CalendarPage() {
  const [date, setDate] = useState(new Date());
  const [meetings, setMeetings] = useState([]);

  useEffect(()=>{ load() },[]);

  async function load(){
    try {
      const data = await fetchMeetings();
      setMeetings(data || []);
    } catch {}
  }

  const meetingsOnDate = meetings.filter(m => {
    if (!m.datetime) return false;
    try {
      const d = new Date(m.datetime);
      return d.toDateString() === date.toDateString();
    } catch { return false; }
  });

  return (
     <div className="calendar-page">
      <div className="calendar-card">
        <Calendar onChange={setDate} value={date} />
      </div>
      <div className="calendar-card">
        <h3 className="meetings-title">Réunions le {date.toDateString()}</h3>
        {meetingsOnDate.length === 0 ? (
          <div className="no-meetings">Aucune réunion</div>
        ) : (
          meetingsOnDate.map(m => (
            <div key={m.id} className="meeting-card">
              <div className="meeting-title">{m.title}</div>
              <div className="meeting-datetime">{m.datetime}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
