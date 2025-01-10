import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

const App = () => {
  const [loggedInUser, setLoggedInUser] = useState(() => {
    // Retrieve the token from localStorage on initial load
    return localStorage.getItem("access_token") ? "Authenticated User" : "";
  });

  const handleLogout = () => {
    setLoggedInUser("");
    localStorage.removeItem("access_token"); // Clear token on logout
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            loggedInUser ? <Navigate to="/dashboard" /> : <Login setLoggedInUser={setLoggedInUser} />
          }
        />
        <Route
          path="/dashboard"
          element={
            loggedInUser ? (
              <Dashboard loggedInUser={loggedInUser} handleLogout={handleLogout} />
            ) : (
              <Navigate to="/" />
            )
          }
        />
      </Routes>
    </Router>
  );
};

export default App;
