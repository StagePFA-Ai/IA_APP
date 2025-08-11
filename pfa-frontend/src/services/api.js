import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 30000
});

export async function loginUser(credentials) {
  // stub: adapte à ton backend
  return { success: true, token: "local-token" };
}

export async function fetchMeetings() {
  const res = await API.get("/meetings");
  return res.data;
}

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
