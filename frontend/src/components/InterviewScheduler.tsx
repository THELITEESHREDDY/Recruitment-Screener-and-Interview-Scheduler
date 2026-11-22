import { useState, type FormEvent } from "react";
import axios from "axios";
import api from "../api/Client";

type Props = {
  jobId: string;
};

type InterviewAssignment = {
  candidate_id: string;
  candidate_name: string;
  rank: number;
  overall_score: number;
  interview_slot: {
    date: string;
    start_time: string;
    end_time: string;
  };
  status: string;
};

type ScheduleResult = {
  schedule?: InterviewAssignment[];
  errors?: string[];
};

const inputClassName =
  "w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-xs text-zinc-900 placeholder-zinc-400 shadow-2xs transition focus:border-indigo-600 focus:outline-none";

const labelClassName = "block text-xs font-semibold text-zinc-800";

export default function InterviewScheduler({ jobId }: Props) {
  const [topN, setTopN] = useState(3);
  const [duration, setDuration] = useState(15);
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("17:00");

  const [result, setResult] = useState<ScheduleResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSchedule(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await api.post(`/jobs/${jobId}/schedule`, {
        mode: "automatic",
        top_n: topN,
        interview_duration_minutes: duration,
        schedule: [],
        start_date: startDate,
        daily_working_hours: {
          start_time: startTime,
          end_time: endTime,
        },
      });
      console.log("Scheduling API Response:", response.data);
      setResult(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;

        setError(
          typeof detail === "string"
            ? detail
            : "Failed to schedule interviews."
        );
      } else {
        setError("Unable to schedule interviews.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-6">
      <form
        onSubmit={handleSchedule}
        className="space-y-5 rounded-md border border-zinc-200 bg-white p-6 shadow-2xs"
      >
        <div className="border-b border-zinc-100 pb-3">
          <h4 className="text-sm font-semibold text-zinc-900">
            Interview Scheduler
          </h4>
          <p className="mt-0.5 text-xs text-zinc-600">
            Automatically assign interview slots for top-ranked candidates.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="space-y-1.5">
            <label htmlFor="top-candidates" className={labelClassName}>
              Top Candidates
            </label>
            <input
              id="top-candidates"
              type="number"
              min={1}
              value={topN}
              onChange={(e) => setTopN(Number(e.target.value))}
              required
              className={inputClassName}
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="interview-duration" className={labelClassName}>
              Interview Duration (minutes)
            </label>
            <input
              id="interview-duration"
              type="number"
              min={1}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              required
              className={inputClassName}
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="start-date" className={labelClassName}>
              Start Date
            </label>
            <input
              id="start-date"
              type="date"
              min={new Date().toLocaleDateString("en-CA")}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
              className={inputClassName}
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="working-hours-start" className={labelClassName}>
              Working Hours Start
            </label>
            <input
              id="working-hours-start"
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              required
              className={inputClassName}
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="working-hours-end" className={labelClassName}>
              Working Hours End
            </label>
            <input
              id="working-hours-end"
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              required
              className={inputClassName}
            />
          </div>
        </div>

        {error && (
          <div
            role="alert"
            className="rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-4 py-3 text-xs font-medium text-red-800"
          >
            {error}
          </div>
        )}

        <div className="pt-1">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex cursor-pointer items-center justify-center rounded-md bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-2xs transition hover:bg-indigo-700 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Scheduling...
              </span>
            ) : (
              "Schedule Interviews"
            )}
          </button>
        </div>
      </form>

      {result !== null && (
        <section className="space-y-4 rounded-md border border-zinc-200 bg-white p-6 shadow-2xs">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div>
              <h4 className="text-sm font-semibold text-zinc-900">
                Interview Schedule
              </h4>
              <p className="mt-0.5 text-xs text-zinc-600">
                Generated interview time slots and assignment status.
              </p>
            </div>
            {result.schedule?.length ? (
              <span className="rounded bg-indigo-50 px-2.5 py-1 font-mono text-[11px] font-semibold text-indigo-700 border border-indigo-200/70">
                {result.schedule.length}{" "}
                {result.schedule.length === 1 ? "slot" : "slots"}
              </span>
            ) : null}
          </div>

          {result.schedule?.length ? (
            <div className="overflow-x-auto rounded-md border border-zinc-200">
              <table className="w-full border-collapse text-left text-xs text-zinc-800">
                <thead>
                  <tr className="border-b border-zinc-200 bg-zinc-50/80 text-[11px] font-semibold uppercase tracking-wider text-zinc-600">
                    <th className="px-4 py-3 text-center">Rank</th>
                    <th className="px-4 py-3">Candidate</th>
                    <th className="px-4 py-3 text-right">Match Score</th>
                    <th className="px-4 py-3">Interview Date</th>
                    <th className="px-4 py-3">Start Time</th>
                    <th className="px-4 py-3">End Time</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-zinc-200">
                  {result.schedule.map((interview) => (
                    <tr
                      key={interview.candidate_id}
                      className="transition hover:bg-zinc-50/80"
                    >
                      <td className="px-4 py-3 text-center font-mono font-semibold text-zinc-900">
                        #{interview.rank}
                      </td>
                      <td className="px-4 py-3 font-semibold text-zinc-900">
                        {interview.candidate_name}
                      </td>
                      <td className="px-4 py-3 text-right font-mono">
                        <span className="inline-block rounded bg-indigo-50 px-2 py-0.5 font-semibold text-indigo-700 border border-indigo-200/60">
                          {interview.overall_score}%
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-[11px] text-zinc-700">
                        {interview.interview_slot?.date ?? "—"}
                      </td>
                      <td className="px-4 py-3 font-mono text-[11px] text-zinc-700">
                        {interview.interview_slot?.start_time ?? "—"}
                      </td>
                      <td className="px-4 py-3 font-mono text-[11px] text-zinc-700">
                        {interview.interview_slot?.end_time ?? "—"}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-block rounded border border-zinc-200 bg-zinc-100 px-2 py-0.5 text-[11px] font-semibold capitalize text-zinc-800">
                          {interview.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50/70 p-6 text-center text-xs text-zinc-500">
              No interviews were scheduled.
            </div>
          )}

          {result.errors?.length ? (
            <div
              role="alert"
              className="space-y-1.5 rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-4 py-3 text-xs text-red-800"
            >
              <h5 className="font-semibold text-red-900">Scheduling Errors</h5>
              {result.errors.map((errMsg, index) => (
                <p key={index} className="font-medium">
                  {errMsg}
                </p>
              ))}
            </div>
          ) : null}
        </section>
      )}
    </section>
  );
}