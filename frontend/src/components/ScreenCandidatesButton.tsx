import { useState } from "react";
import axios from "axios";
import api from "../api/Client";

type Props = {
  jobId: string;
};

export default function ScreenCandidatesButton({ jobId }: Props) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleScreening() {
    setLoading(true);
    setMessage("");
    setError("");

    try {
      const response = await api.post(`/jobs/${jobId}/screen`);

      setMessage(
        response.data.message || "Screening completed successfully."
      );
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;

        setError(
          typeof detail === "string"
            ? detail
            : "Candidate screening failed."
        );
      } else {
        setError("Unable to screen candidates.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-2 sm:items-end">
      <button
        type="button"
        onClick={handleScreening}
        disabled={loading}
        className="inline-flex cursor-pointer items-center justify-center rounded-md bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-2xs transition hover:bg-indigo-700 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            <span>Screening Candidates...</span>
          </span>
        ) : (
          "Screen Candidates"
        )}
      </button>

      {message && (
        <p
          role="status"
          className="rounded-md border border-emerald-200 border-l-4 border-l-emerald-600 bg-emerald-50 px-3 py-2 text-xs font-medium text-emerald-900"
        >
          {message}
        </p>
      )}

      {error && (
        <p
          role="alert"
          className="rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-3 py-2 text-xs font-medium text-red-800"
        >
          {error}
        </p>
      )}
    </div>
  );
}