import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import api from "../api/Client";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      const token = response.data.access_token;

      if (typeof token !== "string" || !token) {
        throw new Error("Login response did not contain an access token");
      }

      sessionStorage.setItem("access_token", token);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;

        setError(
          typeof detail === "string"
            ? detail
            : "Login failed. Please check your credentials."
        );
      } else {
        setError("Unable to complete login.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-12 bg-white font-sans text-zinc-900 antialiased">
      {/* Left Brand Panel */}
      <div className="relative hidden flex-col justify-between border-r border-zinc-200 bg-zinc-50 p-12 lg:flex lg:col-span-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-indigo-600 font-bold text-sm text-white shadow-2xs">
            R
          </div>
          <span className="text-sm font-semibold tracking-wide text-zinc-900">
            Recruitment Screener
          </span>
        </div>

        <div className="space-y-3 max-w-sm">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-indigo-600">
            Hiring Intelligence
          </p>
          <h2 className="text-2xl font-semibold tracking-tight leading-snug text-zinc-900">
            Time is Money, Don't Waste it!
          </h2>
          <p className="text-xs text-zinc-600 leading-relaxed">
            Automate screening, score candidate submissions, and coordinate interview schedules instantly.
          </p>
        </div>

        <div className="text-xs text-zinc-500 font-mono">
          © {new Date().getFullYear()} TalentOS Inc. All rights reserved.
        </div>
      </div>

      {/* Right Form Container */}
      <main className="flex flex-col justify-center px-6 py-12 lg:col-span-7 lg:px-20">
        <div className="mx-auto w-full max-w-sm space-y-8">
          <div className="space-y-1.5">
            <h1 className="text-xl font-semibold tracking-tight text-zinc-900">
              Welcome back
            </h1>
            <p className="text-xs text-zinc-600">
              Enter your work email and password to access your recruiter workspace.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label
                htmlFor="email"
                className="block text-xs font-semibold text-zinc-700"
              >
                Work Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="name@company.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-xs text-zinc-900 placeholder-zinc-400 shadow-2xs transition focus:border-indigo-600 focus:outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label
                  htmlFor="password"
                  className="block text-xs font-semibold text-zinc-700"
                >
                  Password
                </label>
              </div>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-xs text-zinc-900 placeholder-zinc-400 shadow-2xs transition focus:border-indigo-600 focus:outline-none"
              />
            </div>

            {error && (
              <div
                role="alert"
                className="rounded-md border border-red-200 border-l-4 border-l-red-600 bg-red-50 px-3.5 py-2.5 text-xs font-medium text-red-800"
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full cursor-pointer items-center justify-center rounded-md bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-2xs transition hover:bg-indigo-700 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign In to Workspace"}
            </button>
          </form>

          <div className="border-t border-zinc-200 pt-6 text-center text-xs text-zinc-600">
            Need an account?{" "}
            <Link
              to="/register"
              className="font-semibold text-indigo-600 hover:text-indigo-800 underline underline-offset-4"
            >
              Create a recruiter account
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}