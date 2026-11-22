import { type ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { BriefcaseBusiness, LayoutDashboard, LogOut } from "lucide-react";

type Props = {
  children: ReactNode;
};

export default function DashboardLayout({ children }: Props) {
  const navigate = useNavigate();

  function handleLogout() {
    sessionStorage.removeItem("access_token");
    navigate("/login", { replace: true });
  }

  return (
    <div className="flex min-h-screen flex-col bg-white font-sans text-zinc-900 antialiased md:flex-row">
      {/* Sidebar Navigation */}
      <aside className="sticky top-0 z-10 flex w-full flex-col justify-between border-b border-zinc-200 bg-zinc-50 p-6 md:h-screen md:w-64 md:border-r md:border-b-0 shrink-0">
        <div className="space-y-8">
          {/* Brand Header */}
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-indigo-600 text-white shadow-2xs">
              <BriefcaseBusiness size={18} />
            </div>
            <span className="text-sm font-semibold tracking-wide text-zinc-900">
              Recruitment Screener
            </span>
          </div>

          {/* Nav Links */}
          <nav className="space-y-1">
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-md px-3 py-2 text-xs font-semibold transition ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200/60"
                    : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                }`
              }
            >
              <LayoutDashboard size={16} />
              <span>Dashboard</span>
            </NavLink>
          </nav>
        </div>

        {/* Footer / Logout */}
        <div className="pt-6 border-t border-zinc-200 mt-6 md:mt-0">
          <button
            onClick={handleLogout}
            className="flex w-full cursor-pointer items-center gap-2.5 rounded-md px-3 py-2 text-xs font-semibold text-zinc-600 transition hover:bg-rose-50 hover:text-rose-700"
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Workspace Content */}
      <main className="flex-1 px-6 py-8 md:px-10 md:py-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}