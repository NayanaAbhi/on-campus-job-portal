import React from 'react';

const mockJobs = [
  { id: 1, title: 'Library Assistant', applicants: 4 },
  { id: 2, title: 'Fitness Center Attendant', applicants: 2 },
];

const mockShifts = [
  { id: 1, student: 'Alice Johnson', job: 'Library Assistant', hours: 3 },
  { id: 2, student: 'Bob Smith', job: 'Fitness Center Attendant', hours: 2 },
];

function ManagerDashboard() {
  return (
    <div className="container mt-4">
      <h2 className="mb-4 text-center">Manager Dashboard</h2>

      <div className="mb-5">
        <h4>Job Postings</h4>
        <ul className="list-group">
          {mockJobs.map((job) => (
            <li className="list-group-item d-flex justify-content-between align-items-center" key={job.id}>
              {job.title}
              <span className="badge bg-primary rounded-pill">{job.applicants} Applicants</span>
            </li>
          ))}
        </ul>
      </div>

      <div>
        <h4>Assigned Shifts</h4>
        <table className="table table-bordered mt-3">
          <thead>
            <tr>
              <th>Student</th>
              <th>Job</th>
              <th>Hours</th>
            </tr>
          </thead>
          <tbody>
            {mockShifts.map((shift) => (
              <tr key={shift.id}>
                <td>{shift.student}</td>
                <td>{shift.job}</td>
                <td>{shift.hours}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ManagerDashboard;
