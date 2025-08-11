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
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="bg-white p-4 rounded shadow">
        <Calendar onChange={setDate} value={date} />
      </div>
      <div className="bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">Réunions le {date.toDateString()}</h3>
        {meetingsOnDate.length === 0 ? (
          <div className="text-gray-500">Aucune réunion</div>
        ) : (
          meetingsOnDate.map(m => (
            <div key={m.id} className="border p-3 rounded mb-2">
              <div className="font-semibold">{m.title}</div>
              <div className="text-sm text-gray-500">{m.datetime}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
