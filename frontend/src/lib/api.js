import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
  headers: { "Content-Type": "application/json" },
});

export const startAnalysis = async (type = "pulse") => {
  const response = await api.post(`/analysis/start?analysis_type=${type}`);
  return response.data;
};

export const submitPulse = async (data) => {
  const response = await api.post("/analysis/pulse", data);
  return response.data;
};

export const submitBaseline = async (data) => {
  const response = await api.post("/analysis/baseline", data);
  return response.data;
};

export const submitChanges = async (data) => {
  const response = await api.post("/analysis/changes", data);
  return response.data;
};

export const submitTimeline = async (data) => {
  const response = await api.post("/analysis/timeline", data);
  return response.data;
};

export const submitEvidence = async (data) => {
  const response = await api.post("/analysis/evidence", data);
  return response.data;
};

export const getNextQuestion = async (sessionId) => {
  const response = await api.get(`/analysis/${sessionId}/question`);
  return response.data;
};

export const submitAnswer = async (data) => {
  const response = await api.post("/analysis/answer", data);
  return response.data;
};

export const submitMirrorMode = async (data) => {
  const response = await api.post("/analysis/mirror", data);
  return response.data;
};

export const getConversationGuidance = async (data) => {
  const response = await api.post("/analysis/conversation-coach", data);
  return response.data;
};

export const getResults = async (sessionId) => {
  const response = await api.get(`/analysis/${sessionId}/results`);
  return response.data;
};

export const getSessionStatus = async (sessionId) => {
  const response = await api.get(`/analysis/${sessionId}/status`);
  return response.data;
};

export const getTimelineHistory = async () => {
  const response = await api.get("/timeline-history");
  return response.data;
};

export const saveTimelineEntry = async (score, label) => {
  const response = await api.post("/timeline-history", { score, label });
  return response.data;
};

export const createSharedReport = async (reportData) => {
  const response = await api.post("/reports/share", reportData);
  return response.data;
};

export const getSharedReport = async (reportId) => {
  const response = await api.get(`/reports/${reportId}`);
  return response.data;
};
