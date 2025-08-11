import React from "react";

export default function Settings(){
  return (
    <div className="bg-white p-6 rounded shadow">
      <h3 className="font-semibold mb-3">Paramètres</h3>
      <div className="space-y-4 text-sm text-gray-700">
        <div>
          <label className="block mb-1 font-medium">Enregistrement automatique</label>
          <button className="bg-blue-600 text-white px-3 py-1 rounded">Activer</button>
        </div>
        <div>
          <label className="block mb-1 font-medium">Modèle de transcription</label>
          <select className="border p-2 rounded w-full">
            <option>faster-whisper (local)</option>
            <option>whisper (local)</option>
          </select>
        </div>
        <div>
          <label className="block mb-1 font-medium">Options résumé</label>
          <select className="border p-2 rounded w-full">
            <option>mT5 (extractif)</option>
            <option>LLM local (abstractive)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
