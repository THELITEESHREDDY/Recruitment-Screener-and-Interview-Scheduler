import { useState, type FormEvent } from "react";
import axios from "axios";
import api from "../api/Client";

type Job = {
  id: string;
  job_description: string;
  spreadsheet_url: string | null;
};

type Props = {
  onJobCreated: (job: Job) => void;
};

export default function CreateJobForm({ onJobCreated }: Props) {
  const [description, setDescription] = useState("");
  const [spreadsheetUrl, setSpreadsheetUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.post<Job>("/jobs", {
        job_description: description,
        spreadsheet_url: spreadsheetUrl || null,
      });

      onJobCreated(response.data);

      setDescription("");
      setSpreadsheetUrl("");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;

        setError(
          typeof detail === "string" ? detail : "Failed to create job."
        );
      } else {
        setError("Unable to create job.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full space-y-5 rounded-md border border-zinc-200 bg-white p-6 shadow-2xs"
    >
      <div className="border-b border-zinc-100 pb-3">
        <h3 className="text-base font-semibold text-zinc-900">
          Create New Job
        </h3>
        <p className="text-xs text-zinc-600 mt-0.5">
          Add a detailed job description and connect a candidate spreadsheet.
        </p>
      </div>

      <div className="space-y-1.5">
        <label
          htmlFor="job-description"
          className="block text-xs font-semibold text-zinc-800"
        >
          Job Description <span className="text-rose-600">*</span>
        </label>

        <textarea
          id="job-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter the role, required skills, experience, and responsibilities..."
          rows={6}
          required
          className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-xs text-zinc-900 placeholder-zinc-400 shadow-2xs transition focus:border-indigo-600 focus:outline-none"
        />
      </div>

      <div className="space-y-1.5">
        <label
          htmlFor="spreadsheet-url"
          className="block text-xs font-semibold text-zinc-800"
        >
          Google Spreadsheet URL
        </label>

        <input
          id="spreadsheet-url"
          type="url"
          value={spreadsheetUrl}
          onChange={(e) => setSpreadsheetUrl(e.target.value)}
          placeholder="https://docs.google.com/spreadsheets/d/..."
          className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-xs text-zinc-900 placeholder-zinc-400 shadow-2xs transition focus:border-indigo-600 focus:outline-none"
        />

        <p className="text-[11px] text-zinc-500">
          Optional. Provide a public or accessible Google Sheet URL containing candidate submissions.
        </p>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-4 py-3 text-xs font-medium text-red-800"
        >
          {error}
        </div>
      )}

      <div className="pt-2">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex cursor-pointer items-center justify-center rounded-md bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-2xs transition hover:bg-indigo-700 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Creating Job...
            </span>
          ) : (
            "Create Job"
          )}
        </button>
      </div>
    </form>
  );
}