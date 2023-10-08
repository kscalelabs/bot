import axios from "axios";

export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const api = axios.create({
  withCredentials: true,
  baseURL: BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
    Accepts: "application/json",
  },
});
