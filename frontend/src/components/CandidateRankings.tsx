import { Fragment, useState } from "react";
import axios from "axios";
import api from "../api/Client";

type SectionMatch = {
  score: number;
  justification: string;
  matched_items: string[];
  missing_items: string[];
  evidence: string[] | string;
};

type CriterionEvaluation = {
  score: number;
  evidence_status: string;
  justification: string;
};

type RankedCandidate = {
  candidate_id: string;
  candidate_name: string;
  email: string;
  rank: number;
  overall_score: number;
  secondary_score: number;
  one_line_rationale: string;

  match_scores: Record<string, SectionMatch>;

  secondary_details: {
    criteria_scores: Record<string, CriterionEvaluation>;
    overall_justification: string;
    weighted_score?: number;
  };
};

type RankingsResponse = {
  job_id: string;
  total_candidates: number;
  rankings: RankedCandidate[];
};

export default function CandidateRankings({ jobId }: { jobId: string }) {
  const [rankings, setRankings] = useState<RankedCandidate[]>([]);
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedCandidateId, setExpandedCandidateId] = useState<string | null>(null);

  async function handleViewRankings() {
    if (visible) {
      setVisible(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await api.get<RankingsResponse>(
        `/jobs/${jobId}/rankings`
      );

      setRankings(response.data.rankings);
      setVisible(true);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;

        setError(
          typeof detail === "string" ? detail : "Failed to load rankings."
        );
      } else {
        setError("Unable to load rankings.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      {/* Top Toggle Action */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleViewRankings}
          disabled={loading}
          className="inline-flex cursor-pointer items-center justify-center rounded-md border border-zinc-300 bg-white px-3.5 py-2 text-xs font-semibold text-zinc-800 shadow-2xs transition hover:border-zinc-400 hover:bg-zinc-50 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
              Loading Rankings...
            </span>
          ) : visible ? (
            "Hide Rankings"
          ) : (
            "View Rankings"
          )}
        </button>
      </div>

      {/* Error Callout */}
      {error && (
        <div
          role="alert"
          className="rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-4 py-3 text-xs font-medium text-red-800"
        >
          {error}
        </div>
      )}

      {/* Rankings Section */}
      {visible && (
        <div className="space-y-4">
          {rankings.length === 0 ? (
            <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50/70 p-6 text-center text-xs text-zinc-500">
              No ranked candidates available for this position yet.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-md border border-zinc-200 bg-white shadow-2xs">
              <table className="w-full text-left text-xs text-zinc-800 border-collapse">
                <thead>
                  <tr className="border-b border-zinc-200 bg-zinc-50/80 text-[11px] font-semibold uppercase tracking-wider text-zinc-600">
                    <th className="px-4 py-3 w-14 text-center">Rank</th>
                    <th className="px-4 py-3 min-w-35">Candidate</th>
                    <th className="px-4 py-3 min-w-45">Email</th>
                    <th className="px-4 py-3 min-w-25 text-right">Match</th>
                    <th className="px-4 py-3 min-w-25 text-right">Secondary</th>
                    <th className="px-4 py-3 min-w-70">Rationale</th>
                    <th className="px-4 py-3 w-28 text-center">Actions</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-zinc-200">
                  {rankings.map((candidate) => {
                    const isExpanded = expandedCandidateId === candidate.candidate_id;

                    return (
                      <Fragment key={candidate.candidate_id}>
                        <tr className="transition hover:bg-zinc-50/80">
                          <td className="px-4 py-3.5 text-center font-mono font-semibold text-zinc-900">
                            #{candidate.rank}
                          </td>
                          <td className="px-4 py-3.5 font-semibold text-zinc-900">
                            {candidate.candidate_name}
                          </td>
                          <td className="px-4 py-3.5 text-zinc-600 font-mono text-[11px]">
                            {candidate.email}
                          </td>
                          <td className="px-4 py-3.5 text-right font-mono font-medium">
                            <span className="inline-block rounded bg-indigo-50 px-2 py-0.5 text-indigo-700 font-semibold border border-indigo-200/60">
                              {candidate.overall_score}%
                            </span>
                          </td>
                          <td className="px-4 py-3.5 text-right font-mono font-medium">
                            <span className="inline-block rounded bg-zinc-100 px-2 py-0.5 text-zinc-800 border border-zinc-200">
                              {candidate.secondary_score}%
                            </span>
                          </td>
                          <td className="px-4 py-3.5 text-zinc-600 leading-relaxed max-w-md">
                            {candidate.one_line_rationale}
                          </td>
                          <td className="px-4 py-3.5 text-center">
                            <button
                              onClick={() =>
                                setExpandedCandidateId(
                                  isExpanded ? null : candidate.candidate_id
                                )
                              }
                              className="inline-flex cursor-pointer items-center justify-center rounded border border-zinc-300 bg-white px-2.5 py-1 text-[11px] font-semibold text-zinc-800 shadow-2xs transition hover:border-zinc-400 hover:bg-zinc-50"
                            >
                              {isExpanded ? "Hide Details" : "View Details"}
                            </button>
                          </td>
                        </tr>

                        {/* Detailed Expansion Drawer */}
                        {isExpanded && (
                          <tr>
                            <td colSpan={7} className="bg-zinc-50/70 px-6 py-5 border-t border-b border-zinc-200">
                              <div className="space-y-6 max-w-5xl">
                                {/* Section 1: Match Score Breakdown */}
                                <div className="space-y-3">
                                  <h4 className="text-xs font-semibold uppercase tracking-wider text-indigo-600 border-b border-zinc-200 pb-1.5">
                                    Match Score Breakdown
                                  </h4>

                                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                                    {Object.entries(candidate.match_scores ?? {}).map(
                                      ([section, details]) => (
                                        <div
                                          key={section}
                                          className="rounded-md border border-zinc-200 bg-white p-4 shadow-2xs space-y-2"
                                        >
                                          <div className="flex items-center justify-between border-b border-zinc-100 pb-2">
                                            <h5 className="text-xs font-semibold capitalize text-zinc-900">
                                              {section.replaceAll("_", " ")}
                                            </h5>
                                            <span className="rounded bg-indigo-50 px-2 py-0.5 font-mono text-[11px] font-semibold text-indigo-700">
                                              {details.score}/100
                                            </span>
                                          </div>

                                          <p className="text-xs text-zinc-700 leading-relaxed">
                                            <strong className="text-zinc-900 font-semibold">Justification:</strong>{" "}
                                            {details.justification}
                                          </p>

                                          <div className="space-y-1 pt-1 text-[11px]">
                                            <div className="text-emerald-700">
                                              <strong className="font-semibold text-emerald-800">Matched:</strong>{" "}
                                              {details.matched_items?.join(", ") || "None"}
                                            </div>

                                            <div className="text-rose-700">
                                              <strong className="font-semibold text-rose-800">Missing:</strong>{" "}
                                              {details.missing_items?.join(", ") || "None"}
                                            </div>

                                            <div className="text-zinc-600">
                                              <strong className="font-semibold text-zinc-800">Evidence:</strong>{" "}
                                              {Array.isArray(details.evidence)
                                                ? details.evidence.join(", ")
                                                : details.evidence || "None"}
                                            </div>
                                          </div>
                                        </div>
                                      )
                                    )}
                                  </div>
                                </div>

                                {/* Section 2: Secondary Evaluation */}
                                <div className="space-y-3">
                                  <h4 className="text-xs font-semibold uppercase tracking-wider text-indigo-600 border-b border-zinc-200 pb-1.5">
                                    Secondary Evaluation Criteria
                                  </h4>

                                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                                    {Object.entries(
                                      candidate.secondary_details?.criteria_scores ?? {}
                                    ).map(([criterion, details]) => (
                                      <div
                                        key={criterion}
                                        className="rounded-md border border-zinc-200 bg-white p-3.5 shadow-2xs space-y-1.5"
                                      >
                                        <div className="flex items-center justify-between">
                                          <h5 className="text-xs font-semibold capitalize text-zinc-900">
                                            {criterion.replaceAll("_", " ")}
                                          </h5>
                                          <span className="rounded bg-zinc-100 px-2 py-0.5 font-mono text-[11px] font-semibold text-zinc-800">
                                            {details.score}/100
                                          </span>
                                        </div>

                                        <p className="text-[11px] text-zinc-500 font-medium">
                                          Evidence status:{" "}
                                          <span className="text-zinc-800 capitalize">
                                            {details.evidence_status}
                                          </span>
                                        </p>

                                        <p className="text-xs text-zinc-700 leading-relaxed">
                                          {details.justification}
                                        </p>
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                {/* Section 3: Overall Summary */}
                                {candidate.secondary_details?.overall_justification && (
                                  <div className="rounded-md border border-zinc-200 bg-white p-4 shadow-2xs space-y-1">
                                    <h4 className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
                                      Overall Executive Evaluation
                                    </h4>
                                    <p className="text-xs text-zinc-800 leading-relaxed">
                                      {candidate.secondary_details.overall_justification}
                                    </p>
                                  </div>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}