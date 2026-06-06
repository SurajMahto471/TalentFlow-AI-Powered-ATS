import { useState } from "react";
import { Navigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Briefcase, Loader2, LogIn, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";

type AuthTab = "login" | "signup";

export function Login() {
  const { login, register, isAuthenticated, isLoading } = useAuth();
  const [tab, setTab] = useState<AuthTab>("login");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const [signupName, setSignupName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPhone, setSignupPhone] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupConfirm, setSignupConfirm] = useState("");

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);
    try {
      await login(loginEmail, loginPassword);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (signupPassword !== signupConfirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      const message = await register(signupName, signupEmail, signupPassword, signupPhone);
      setSuccess(message);
      setTab("login");
      setLoginEmail(signupEmail);
      setSignupPassword("");
      setSignupConfirm("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/30 to-background flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg">
            <Briefcase className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">TalentFlow ATS</h1>
          <p className="mt-2 text-muted-foreground">
            Sign in to access the AI-powered recruiter dashboard
          </p>
        </div>

        <Card className="shadow-xl border-border/60">
          <CardHeader className="pb-4">
            <div className="grid grid-cols-2 gap-2 rounded-lg bg-muted p-1">
              <button
                type="button"
                onClick={() => { setTab("login"); setError(""); setSuccess(""); }}
                className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  tab === "login" ? "bg-background shadow text-foreground" : "text-muted-foreground"
                }`}
              >
                Login
              </button>
              <button
                type="button"
                onClick={() => { setTab("signup"); setError(""); setSuccess(""); }}
                className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  tab === "signup" ? "bg-background shadow text-foreground" : "text-muted-foreground"
                }`}
              >
                Sign Up
              </button>
            </div>
            <CardTitle className="pt-2">{tab === "login" ? "Welcome back" : "Create account"}</CardTitle>
            <CardDescription>
              {tab === "login"
                ? "Enter your credentials to continue"
                : "Register to start screening candidates"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}
            {success && (
              <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-900/20 dark:text-emerald-400">
                {success}
              </div>
            )}

            {tab === "login" ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <Input
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="you@company.com"
                    required
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <Input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className="mt-1"
                  />
                </div>
                <Button type="submit" className="w-full" disabled={submitting}>
                  {submitting ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <LogIn className="h-4 w-4 mr-2" />
                  )}
                  Login
                </Button>
              </form>
            ) : (
              <form onSubmit={handleSignup} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Full Name</label>
                  <Input
                    value={signupName}
                    onChange={(e) => setSignupName(e.target.value)}
                    placeholder="Jane Recruiter"
                    required
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <Input
                    type="email"
                    value={signupEmail}
                    onChange={(e) => setSignupEmail(e.target.value)}
                    placeholder="you@company.com"
                    required
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Phone (optional)</label>
                  <Input
                    value={signupPhone}
                    onChange={(e) => setSignupPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <Input
                    type="password"
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    required
                    minLength={6}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Confirm Password</label>
                  <Input
                    type="password"
                    value={signupConfirm}
                    onChange={(e) => setSignupConfirm(e.target.value)}
                    placeholder="Repeat password"
                    required
                    className="mt-1"
                  />
                </div>
                <Button type="submit" className="w-full" disabled={submitting}>
                  {submitting ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <UserPlus className="h-4 w-4 mr-2" />
                  )}
                  Create Account
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Each account has its own isolated screening data. Sign up or log in to get started.
        </p>
      </motion.div>
    </div>
  );
}
