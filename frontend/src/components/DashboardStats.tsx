import { BriefcaseBusiness, Users } from "lucide-react";

type Props = {
  totalJobs: number;
};

export default function DashboardStats({ totalJobs }: Props) {
  return (
    <section
      aria-label="Key recruitment metrics"
      className="grid grid-cols-1 gap-4 sm:grid-cols-2"
    >
      <div className="flex items-center justify-between rounded-md border border-zinc-200 bg-white px-5 py-4 shadow-2xs transition hover:border-zinc-300">
        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
            Total Jobs
          </p>
          <p className="font-mono text-2xl font-semibold tracking-tight text-zinc-900">
            {totalJobs}
          </p>
        </div>

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-indigo-200/70 bg-indigo-50 text-indigo-600">
          <BriefcaseBusiness size={18} />
        </div>
      </div>

      <div className="flex items-center justify-between rounded-md border border-zinc-200 bg-white px-5 py-4 shadow-2xs transition hover:border-zinc-300">
        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
            Recruitment
          </p>
          <div className="flex items-center gap-2 pt-0.5">
            <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden="true" />
            <span className="text-base font-semibold tracking-tight text-zinc-900">
              Active
            </span>
          </div>
        </div>

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-zinc-200 bg-zinc-50 text-zinc-700">
          <Users size={18} />
        </div>
      </div>
    </section>
  );
}