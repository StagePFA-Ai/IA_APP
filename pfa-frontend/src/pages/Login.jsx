import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/api";
import './Login.css'
export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await loginUser({ username, password });
      if (res && res.success) {
        // Tu peux sauver token dans localStorage si tu as un vrai backend
        navigate("/dashboard");
      } else {
        setError("Identifiants incorrects");
      }
    } catch (err) {
      setError("Erreur de connexion");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <div className="w-full max-w-md bg-white p-6 rounded shadow">
        <h2 className="text-2xl font-semibold mb-4">Se connecter</h2>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-3">
          <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Nom d'utilisateur" className="w-full border p-2 rounded" />
          <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Mot de passe" className="w-full border p-2 rounded" />
          <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded">Connexion</button>
        </form>
      </div>
    </div>
  );
}
