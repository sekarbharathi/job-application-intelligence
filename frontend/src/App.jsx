
import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8002/applications/";

const initialForm = {
  company: "",
  job_title: "",
  job_url: "",
  location: "",
  source: "",
  application_date: new Date().toISOString().split("T")[0],
  status: "Applied",
  resume_version: "",
  job_description: "",
  notes: "",
};

function App() {
  const [applications, setApplications] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  async function fetchApplications() {
    try {
      const response = await fetch(API_URL);

      if (!response.ok) {
        throw new Error("Could not load applications.");
      }

      const data = await response.json();
      setApplications(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchApplications();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(
          error.detail
            ? JSON.stringify(error.detail)
            : "Could not save the application."
        );
      }

      setForm({
        ...initialForm,
        application_date: new Date().toISOString().split("T")[0],
      });

      setMessage("Application added successfully.");
      await fetchApplications();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main>
      <h1>Job Application Intelligence</h1>
      <p>Track your job applications in one place.</p>

      <section>
        <h2>Add an application</h2>

        <form onSubmit={handleSubmit}>
          <label>
            Company *
            <input
              name="company"
              value={form.company}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Job title *
            <input
              name="job_title"
              value={form.job_title}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Application date *
            <input
              type="date"
              name="application_date"
              value={form.application_date}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Status
            <select
              name="status"
              value={form.status}
              onChange={handleChange}
            >
              <option value="Applied">Applied</option>
              <option value="Interview">Interview</option>
              <option value="Rejected">Rejected</option>
              <option value="Offer">Offer</option>
              <option value="Withdrawn">Withdrawn</option>
            </select>
          </label>

          <label>
            Location
            <input
              name="location"
              value={form.location}
              onChange={handleChange}
            />
          </label>

          <label>
            Application source
            <input
              name="source"
              placeholder="e.g. LinkedIn, company website"
              value={form.source}
              onChange={handleChange}
            />
          </label>

          <label>
            Job URL
            <input
              type="url"
              name="job_url"
              value={form.job_url}
              onChange={handleChange}
            />
          </label>

          <label>
            Resume version
            <input
              name="resume_version"
              value={form.resume_version}
              onChange={handleChange}
            />
          </label>

          <label>
            Job description
            <textarea
              name="job_description"
              value={form.job_description}
              onChange={handleChange}
              rows={4}
            />
          </label>

          <label>
            Notes
            <textarea
              name="notes"
              value={form.notes}
              onChange={handleChange}
              rows={3}
            />
          </label>

          <button type="submit">Add application</button>
        </form>

        {message && <p role="status">{message}</p>}
      </section>

      <section>
        <h2>Applications ({applications.length})</h2>

        {loading ? (
          <p>Loading applications...</p>
        ) : applications.length === 0 ? (
          <p>No applications yet. Add your first application above.</p>
        ) : (
          applications.map((application) => (
            <article key={application.id}>
              <h3>
                {application.job_title} — {application.company}
              </h3>
              <p>Status: {application.status}</p>
              <p>Applied: {application.application_date}</p>
              {application.location && (
                <p>Location: {application.location}</p>
              )}
              {application.source && <p>Source: {application.source}</p>}
            </article>
          ))
        )}
      </section>
    </main>
  );
}

export default App;