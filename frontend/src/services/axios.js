import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://127.0.0.1:5000/api", // Ensure this matches your backend API prefix
});

// Add an interceptor to include the Authorization header
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); // Match the key in Login.js
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log("Authorization header added:", config.headers.Authorization); // Debugging
  }
  return config;
});

export default axiosInstance;
