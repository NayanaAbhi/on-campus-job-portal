import React, { useEffect, useState } from 'react';

const mockShifts = [
  { id: 1, date: '2025-04-15', time: '10:00 AM - 1:00 PM', job: 'Library Assistant', hours: 3 },
  { id: 2, date: '2025-04-17', time: '2:00 PM - 5:00 PM', job: 'IT Help Desk Intern', hours: 3 },
];

const mockAppliedJobs = [
  { id: 1, title: 'Lab Assistant', status: 'Pending' },
  { id: 2, title: 'Rec Center Staff', status: 'Accepted' },
];

function Dashboard() {
  const totalHours = mockShifts.reduce((sum, shift) => sum + shift.hours, 0);
  const hourlyRate = 15;
  const totalEarnings = totalHours * hourlyRate;

  return (
    <div className="container mt-4">
      <h2 className="text-center mb-4">My Dashboard</h2>

      <div className="accordion" id="studentAccordion">

        {/* Schedule */}
        <div className="accordion-item">
          <h2 className="accordion-header" id="headingSchedule">
            <button className="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseSchedule">
              My Schedule
            </button>
          </h2>
          <div id="collapseSchedule" className="accordion-collapse collapse show" data-bs-parent="#studentAccordion">
            <div className="accordion-body">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Job</th>
                    <th>Hours</th>
                  </tr>
                </thead>
                <tbody>
                  {mockShifts.map((shift) => (
                    <tr key={shift.id}>
                      <td>{shift.date}</td>
                      <td>{shift.time}</td>
                      <td>{shift.job}</td>
                      <td>{shift.hours}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Total Work Summary */}
        <div className="accordion-item">
          <h2 className="accordion-header" id="headingSummary">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseSummary">
              Total Work Summary
            </button>
          </h2>
          <div id="collapseSummary" className="accordion-collapse collapse" data-bs-parent="#studentAccordion">
            <div className="accordion-body">
              <h5>Total Hours Worked: {totalHours}</h5>
              <h5>Total Earnings: ${totalEarnings.toFixed(2)}</h5>
            </div>
          </div>
        </div>

        {/* Career */}
        <div className="accordion-item">
          <h2 className="accordion-header" id="headingCareer">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseCareer">
              Career Opportunities
            </button>
          </h2>
          <div id="collapseCareer" className="accordion-collapse collapse" data-bs-parent="#studentAccordion">
            <div className="accordion-body">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Job Title</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {mockAppliedJobs.map((job) => (
                    <tr key={job.id}>
                      <td>{job.title}</td>
                      <td>{job.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default Dashboard;
