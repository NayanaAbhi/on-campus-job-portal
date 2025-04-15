import React, { useEffect, useState } from 'react';

const mockJobs = [
  {
    id: 1,
    title: 'Library Assistant',
    department: 'Library Services',
    hoursPerWeek: 10,
    description: 'Assist with front desk, shelving, and book checkouts.',
  },
  {
    id: 2,
    title: 'IT Help Desk Intern',
    department: 'IT Department',
    hoursPerWeek: 15,
    description: 'Provide tech support for students and faculty.',
  },
  {
    id: 3,
    title: 'Fitness Center Attendant',
    department: 'WREC',
    hoursPerWeek: 8,
    description: 'Supervise equipment and assist members.',
  },
];

function JobListings() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    // Simulating API call for now
    setJobs(mockJobs);
  }, []);

  return (
    <div className="container mt-4">
      <h2 className="mb-4 text-center">Available On-Campus Jobs</h2>
      <div className="row">
        {jobs.map((job) => (
          <div className="col-md-4 mb-4" key={job.id}>
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">{job.title}</h5>
                <h6 className="card-subtitle mb-2 text-muted">{job.department}</h6>
                <p className="card-text">{job.description}</p>
                <p><strong>Hours/Week:</strong> {job.hoursPerWeek}</p>
                <button className="btn btn-primary w-100">Apply</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default JobListings;
