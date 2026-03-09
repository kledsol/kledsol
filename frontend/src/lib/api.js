import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
  headers: {
    "Content-Type": "application/json",
  },
});

// Analysis API functions
export const startAnalysis = async () => {
  const response = await api.post("/analysis/start");
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

export const getNextQuestion = async (sessionId) => {
  const response = await api.get(`/analysis/${sessionId}/question`);
  return response.data;
};

export const submitAnswer = async (data) => {
  const response = await api.post("/analysis/answer", data);
  return response.data;
};

export const submitReaction = async (data) => {
  const response = await api.post("/analysis/reaction", data);
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
