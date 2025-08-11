import React from "react";

export default function MeetingCard({ meeting, onUpload, onProcess, onView }) {
  return (
    <div className="bg-white p-4 rounded shadow flex justify-between items-start">
      <div>
        <div className="font-semibold">{meeting.title || "Réunion sans titre"}</div>
        <div className="text-sm text-gray-500">Status: {meeting.status || "pending"}</div>
        {meeting.summary && <div className="mt-2 text-sm text-gray-700">Résumé: {meeting.summary}</div>}
      </div>

      <div className="flex flex-col items-end gap-2">
        <input type="file" accept="audio/*" onChange={e => onUpload(meeting.id, e.target.files[0])} />
        <div className="flex gap-2">
          <button onClick={() => onProcess(meeting.id)} className="bg-green-600 text-white px-3 py-1 rounded text-sm">Traiter</button>
          <button onClick={() => onView(meeting.id)} className="bg-gray-200 px-3 py-1 rounded text-sm">Voir</button>
        </div>
      </div>
    </div>
  );
}
