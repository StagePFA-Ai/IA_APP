import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 30000,
});

// Intercepteur pour ajouter le token JWT aux requêtes
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});



const API_URL = "http://localhost:8000/api/";

export const loginUser = async (credentials) => {
  try {
    const response = await axios.post(`${API_URL}login/`, credentials);
    return response.data; // { access, refresh }
  } catch (error) {
    console.error("Erreur de connexion", error);
    return null;
  }
};

export async function fetchMeetings() {
  const res = await fetch("http://localhost:8000/api/meetings/");
  if (!res.ok) throw new Error("Erreur API");
  return res.json();}

export async function createMeeting(payload) {
  const res = await API.post("/meetings", payload);
  return res.data;
}

export async function uploadAudio(meetingId, file) {
  const form = new FormData();
  form.append("file", file);
  const res = await API.post(`/meetings/${meetingId}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return res.data;
}

export async function processMeeting(meetingId) {
  const res = await API.post(`/meetings/${meetingId}/process`);
  return res.data;
}

export async function getMeeting(id) {
  const res = await API.get(`/meetings/${id}`);
  return res.data;
}
