import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import JobListings from './pages/JobListings';
import ManagerDashboard from './pages/ManagerDashboard';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <Navbar />
      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/jobs" element={<JobListings />} />
          <Route path="/manager" element={<ManagerDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
