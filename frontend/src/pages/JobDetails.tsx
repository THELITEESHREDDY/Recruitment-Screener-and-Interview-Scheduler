import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";
import api from "../api/Client";

import DashboardLayout from "../components/DashboardLayout";
import ScreenCandidatesButton from "../components/ScreenCandidatesButton";
import CandidateRankings from "../components/CandidateRankings";
import InterviewScheduler from "../components/InterviewScheduler";

type Job = {
  id: string;
  job_description: string;
  spreadsheet_url: string | null;
};

export default function JobDetails() {
  const { jobId } = useParams<{ jobId: string }>();

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!jobId) {
      setError("Invalid job ID.");
      setLoading(false);
      return;
    }

    async function fetchJob() {
      try {
        const response = await api.get<Job>(`/jobs/${jobId}`);
        setJob(response.data);
      } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 404) {
          setError("Job not found.");
        } else {
          setError("Failed to load job details.");
        }
      } finally {
        setLoading(false);
      }
    }

    void fetchJob();
  }, [jobId]);

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-7xl space-y-8 text-zinc-900">
        {/* Top Navigation Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-xs font-medium text-zinc-800 shadow-2xs transition hover:border-zinc-400 hover:bg-zinc-50"
          >
            <span aria-hidden="true">&larr;</span>
            <span>Back to Roles</span>
          </Link>

          {job && (
            <span className="font-mono text-xs text-zinc-500">
              ID: {job.id}
            </span>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center gap-2.5 border-y border-zinc-200 py-10 text-xs font-medium text-zinc-600">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
            <span>Loading role configuration...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div
            role="alert"
            className="rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-4 py-3 text-xs font-medium text-red-800"
          >
            {error}
          </div>
        )}

        {job && (
          <>
            {/* Page Header & Primary Action */}
            <header className="flex flex-col justify-between gap-4 border-b border-zinc-200 pb-5 sm:flex-row sm:items-end [&_button]:inline-flex [&_button]:cursor-pointer [&_button]:items-center [&_button]:justify-center [&_button]:rounded-md [&_button]:bg-indigo-600 [&_button]:px-4 [&_button]:py-2 [&_button]:text-xs [&_button]:font-semibold [&_button]:text-white [&_button]:shadow-xs [&_button]:transition hover:[&_button]:bg-indigo-700 [&_button]:disabled:cursor-not-allowed [&_button]:disabled:opacity-50">
              <div className="space-y-1">
                <p className="text-[11px] font-semibold uppercase tracking-widest text-indigo-600">
                  Hiring Pipeline
                </p>
                <h1 className="text-xl font-semibold tracking-tight text-zinc-900">
                  Role Overview &amp; Evaluation
                </h1>
              </div>

              <div className="shrink-0">
                <ScreenCandidatesButton jobId={job.id} />
              </div>
            </header>

            {/* Specification Rows */}
            <section
              aria-label="Role specifications"
              className="divide-y divide-zinc-200 border-b border-zinc-200"
            >
              <div className="grid grid-cols-1 gap-2 py-3.5 sm:grid-cols-12 sm:items-center sm:gap-4">
                <span className="text-xs font-semibold text-zinc-700 sm:col-span-3">
                  Reference ID
                </span>
                <div className="sm:col-span-9">
                  <code className="rounded bg-zinc-900 px-2.5 py-1 font-mono text-xs text-zinc-100">
                    {job.id}
                  </code>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-2 py-3.5 sm:grid-cols-12 sm:items-center sm:gap-4">
                <span className="text-xs font-semibold text-zinc-700 sm:col-span-3">
                  Candidate Sheet
                </span>
                <div className="min-w-0 sm:col-span-9">
                  {job.spreadsheet_url ? (
                    <a
                      href={job.spreadsheet_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-block max-w-full truncate text-xs font-medium text-indigo-600 underline underline-offset-4 hover:text-indigo-800"
                    >
                      {job.spreadsheet_url}
                    </a>
                  ) : (
                    <span className="text-xs font-medium text-zinc-500">
                      Not connected
                    </span>
                  )}
                </div>
              </div>

              <div className="py-3.5">
                <details className="group">
                  <summary className="flex cursor-pointer list-none items-center justify-between rounded-md py-1 text-xs font-semibold text-zinc-800 transition hover:text-indigo-700 [&::-webkit-details-marker]:hidden">
                    <span>Job Description</span>
                    <span className="rounded border border-zinc-300 bg-zinc-50 px-2.5 py-1 text-[11px] font-medium text-zinc-700 group-open:hidden">
                      Expand brief
                    </span>
                    <span className="hidden rounded border border-zinc-300 bg-zinc-100 px-2.5 py-1 text-[11px] font-medium text-zinc-800 group-open:inline">
                      Collapse brief
                    </span>
                  </summary>

                  <div className="mt-3 rounded-md border border-zinc-200 bg-zinc-50 p-4">
                    <p className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-zinc-800">
                      {job.job_description}
                    </p>
                  </div>
                </details>
              </div>
            </section>

            {/* Full-Width Candidate Rankings Section */}
            <section
              aria-label="Candidate Rankings and Evaluations"
              className="space-y-4 border-b border-zinc-200 pb-8 [&_table]:w-full [&_table]:border-collapse [&_th]:whitespace-nowrap [&_th]:bg-zinc-50 [&_th]:px-3.5 [&_th]:py-2.5 [&_th]:text-left [&_th]:text-[11px] [&_th]:font-semibold [&_th]:uppercase [&_th]:tracking-wider [&_th]:text-zinc-600 [&_td]:border-t [&_td]:border-zinc-200 [&_td]:px-3.5 [&_td]:py-3 [&_td]:align-top [&_td]:text-xs [&_td]:text-zinc-800 [&_button]:inline-flex [&_button]:cursor-pointer [&_button]:items-center [&_button]:justify-center [&_button]:rounded-md [&_button]:border [&_button]:border-zinc-300 [&_button]:bg-white [&_button]:px-3 [&_button]:py-1.5 [&_button]:text-xs [&_button]:font-semibold [&_button]:text-zinc-900 [&_button]:shadow-2xs [&_button]:transition hover:[&_button]:border-zinc-400 hover:[&_button]:bg-zinc-50"
            >
              <div className="flex items-baseline justify-between border-b border-zinc-200 pb-3">
                <div>
                  <h2 className="text-sm font-semibold text-zinc-900">
                    Candidate Rankings &amp; Evaluations
                  </h2>
                  <p className="text-xs text-zinc-600">
                    Scored submissions, rationales, and role-fit assessments
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <CandidateRankings jobId={job.id} />
              </div>
            </section>

            {/* Dedicated Interview Scheduling Section */}
            <section
              aria-label="Interview Scheduling"
              className="max-w-3xl space-y-4 [&_input]:mt-1.5 [&_input]:w-full [&_input]:rounded-md [&_input]:border [&_input]:border-zinc-300 [&_input]:bg-white [&_input]:px-3 [&_input]:py-2 [&_input]:text-xs [&_input]:text-zinc-900 [&_input]:shadow-2xs focus:[&_input]:border-indigo-600 focus:[&_input]:outline-none [&_label]:block [&_label]:text-xs [&_label]:font-semibold [&_label]:text-zinc-800 [&_button]:mt-3 [&_button]:inline-flex [&_button]:cursor-pointer [&_button]:items-center [&_button]:justify-center [&_button]:rounded-md [&_button]:bg-zinc-900 [&_button]:px-4 [&_button]:py-2.5 [&_button]:text-xs [&_button]:font-semibold [&_button]:text-white [&_button]:shadow-2xs [&_button]:transition hover:[&_button]:bg-zinc-800"
            >
              <div className="flex items-baseline justify-between border-b border-zinc-200 pb-3">
                <div>
                  <h2 className="text-sm font-semibold text-zinc-900">
                    Interview Scheduling
                  </h2>
                  <p className="text-xs text-zinc-600">
                    Configure candidate batch size, duration, dates, and interview hours
                  </p>
                </div>
              </div>

              <InterviewScheduler jobId={job.id} />
            </section>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}