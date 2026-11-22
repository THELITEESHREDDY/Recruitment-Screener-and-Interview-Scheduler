import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import CreateJobForm from "../components/CreateJobForm";
import api from "../api/Client";
import DashboardLayout from "../components/DashboardLayout";
import DashboardStats from "../components/DashboardStats";

type Job = {
  id: string;
  job_description: string;
  spreadsheet_url: string | null;
};

export default function Dashboard() {
  const navigate = useNavigate();

  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function fetchJobs() {
      try {
        const response = await api.get<Job[]>("/jobs");

        if (active) {
          setJobs(response.data);
        }
      } catch (err) {
        if (!active) return;

        if (axios.isAxiosError(err) && err.response?.status === 401) {
          sessionStorage.removeItem("access_token");
          navigate("/login", { replace: true });
          return;
        }

        setError("Failed to load jobs.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    fetchJobs();

    return () => {
      active = false;
    };
  }, [navigate]);

  function handleJobCreated(job: Job) {
    setJobs((previousJobs) => [job, ...previousJobs]);
  }

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl space-y-8 text-zinc-900">
        {/* Page Header */}
        <header className="flex flex-col justify-between gap-2 border-b border-zinc-200 pb-5 sm:flex-row sm:items-end">
          <div className="space-y-1">
            <p className="text-[11px] font-semibold uppercase tracking-widest text-indigo-600">
              Hiring Workspace
            </p>
            <h1 className="text-xl font-semibold tracking-tight text-zinc-900">
              Recruiter Dashboard
            </h1>
          </div>

          {!loading && !error && (
            <span className="font-mono text-xs text-zinc-500">
              {jobs.length} {jobs.length === 1 ? "active role" : "active roles"}
            </span>
          )}
        </header>

        {/* Stats Strip */}
        <section
          aria-label="Dashboard metrics"
          className="[&_dl]:grid [&_dl]:grid-cols-1 [&_dl]:divide-y [&_dl]:divide-zinc-200 [&_dl]:overflow-hidden [&_dl]:rounded-md [&_dl]:border [&_dl]:border-zinc-200 [&_dl]:bg-white sm:[&_dl]:grid-cols-3 sm:[&_dl]:divide-x sm:[&_dl]:divide-y-0 [&>div]:grid [&>div]:grid-cols-1 [&>div]:gap-4 sm:[&>div]:grid-cols-3"
        >
          <DashboardStats totalJobs={jobs.length} />
        </section>

        {/* Create New Job Section */}
        <section
          aria-label="Create job"
          className="space-y-4 border-b border-zinc-200 pb-8 [&_input]:mt-1.5 [&_input]:w-full [&_input]:rounded-md [&_input]:border [&_input]:border-zinc-300 [&_input]:bg-white [&_input]:px-3 [&_input]:py-2 [&_input]:text-xs [&_input]:text-zinc-900 [&_input]:shadow-2xs focus:[&_input]:border-indigo-600 focus:[&_input]:outline-none [&_textarea]:mt-1.5 [&_textarea]:w-full [&_textarea]:rounded-md [&_textarea]:border [&_textarea]:border-zinc-300 [&_textarea]:bg-white [&_textarea]:px-3 [&_textarea]:py-2 [&_textarea]:text-xs [&_textarea]:text-zinc-900 [&_textarea]:shadow-2xs focus:[&_textarea]:border-indigo-600 focus:[&_textarea]:outline-none [&_select]:mt-1.5 [&_select]:w-full [&_select]:rounded-md [&_select]:border [&_select]:border-zinc-300 [&_select]:bg-white [&_select]:px-3 [&_select]:py-2 [&_select]:text-xs [&_select]:text-zinc-900 [&_select]:shadow-2xs focus:[&_select]:border-indigo-600 focus:[&_select]:outline-none [&_label]:block [&_label]:text-xs [&_label]:font-semibold [&_label]:text-zinc-800 [&_button[type='submit']]:mt-3 [&_button[type='submit']]:inline-flex [&_button[type='submit']]:cursor-pointer [&_button[type='submit']]:items-center [&_button[type='submit']]:justify-center [&_button[type='submit']]:rounded-md [&_button[type='submit']]:bg-indigo-600 [&_button[type='submit']]:px-4 [&_button[type='submit']]:py-2 [&_button[type='submit']]:text-xs [&_button[type='submit']]:font-semibold [&_button[type='submit']]:text-white [&_button[type='submit']]:shadow-xs [&_button[type='submit']]:transition hover:[&_button[type='submit']]:bg-indigo-700 [&_button[type='submit']]:disabled:cursor-not-allowed [&_button[type='submit']]:disabled:opacity-50"
        >
          <div className="border-b border-zinc-200 pb-3">
            <h2 className="text-sm font-semibold text-zinc-900">
              Post a New Role
            </h2>
            <p className="text-xs text-zinc-600">
              Add a job brief and optional candidate sheet to start screening
            </p>
          </div>

          <div className="w-full">
            <CreateJobForm onJobCreated={handleJobCreated} />
          </div>
        </section>

        {/* Jobs List Section */}
        <section aria-label="Your Jobs" className="space-y-4">
          <div className="flex items-baseline justify-between border-b border-zinc-200 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-zinc-900">
                Your Jobs
              </h2>
              <p className="text-xs text-zinc-600">
                Select a role to review candidate rankings or schedule interviews
              </p>
            </div>
          </div>

          {loading && (
            <div className="flex items-center gap-2.5 border-y border-zinc-200 py-10 text-xs font-medium text-zinc-600">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
              <span>Loading jobs...</span>
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-4 py-3 text-xs font-medium text-red-800"
            >
              {error}
            </div>
          )}

          {!loading && !error && jobs.length === 0 && (
            <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50/70 px-6 py-10 text-center">
              <p className="text-xs font-semibold text-zinc-800">
                No jobs created yet.
              </p>
              <p className="mt-1 text-xs text-zinc-500">
                Use the form above to publish your first role and begin candidate evaluations.
              </p>
            </div>
          )}

          {!loading && !error && jobs.length > 0 && (
            <div className="divide-y divide-zinc-200 overflow-hidden rounded-md border border-zinc-200 bg-white">
              {jobs.map((job) => (
                <article
                  key={job.id}
                  className="transition hover:bg-zinc-50/90"
                >
                  <Link
                    to={`/jobs/${job.id}`}
                    className="group flex flex-col justify-between gap-4 px-5 py-4 sm:flex-row sm:items-center"
                  >
                    <div className="min-w-0 flex-1 space-y-1.5">
                      <h3 className="text-sm font-semibold leading-snug text-zinc-900 transition-colors group-hover:text-indigo-700">
                        {job.job_description.length > 130
                          ? `${job.job_description.slice(0, 130)}...`
                          : job.job_description}
                      </h3>

                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-500">
                        <span>
                          Job ID:{" "}
                          <code className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono text-[11px] text-zinc-700">
                            {job.id}
                          </code>
                        </span>
                        {job.spreadsheet_url && (
                          <span className="font-medium text-emerald-700">
                            Sheet connected
                          </span>
                        )}
                      </div>
                    </div>

                    <span className="inline-flex shrink-0 items-center gap-1.5 self-start rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-xs font-semibold text-zinc-800 shadow-2xs transition group-hover:border-indigo-600 group-hover:bg-indigo-600 group-hover:text-white sm:self-center">
                      <span>View Job Details</span>
                      <span aria-hidden="true">&rarr;</span>
                    </span>
                  </Link>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}