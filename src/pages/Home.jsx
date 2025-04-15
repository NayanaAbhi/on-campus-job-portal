import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="text-center">
      <h1 className="display-4 mt-5">Welcome to the On-Campus Job Portal</h1>
      <p className="lead mt-3">
        Discover jobs, manage your shifts, and stay on top of your academic and work schedule.
      </p>
      <Link to="/jobs" className="btn btn-primary btn-lg mt-4">
        Browse Jobs
      </Link>
    </div>
  );
}

export default Home;
