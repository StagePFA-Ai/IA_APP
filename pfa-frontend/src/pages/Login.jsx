import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/api";


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
    if (res && res.access) {
      localStorage.setItem("access_token", res.access);
      localStorage.setItem("refresh_token", res.refresh);
      navigate("/dashboard");
    } else {
      setError("Identifiants incorrects");
    }
  } catch (err) {
    setError("Erreur de connexion");
  }
};
  return (
    <div className="login-container">
      <div className="login-box">
        
        <h2>Se connecter</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit} className="login-form">
          <input
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Nom d'utilisateur"
          />
          <input
            value={password}
            onChange={e => setPassword(e.target.value)}
            type="password"
            placeholder="Mot de passe"
          />
          <button type="submit">Connexion</button>
        </form>
        
        <div className="login-footer">
          <p>Pas encore de compte ? <a href="/register">S'inscrire</a></p>
          <p><a href="/forgot-password">Mot de passe oublié ?</a></p>
        </div>
      </div>
    </div>
  );
}
