import type { Candidate, DashboardStats } from "@/types";

export interface ScreeningJob {
  title: string;
  rawText: string;
  requiredSkills: string[];
  experienceRequired: number;
}

export interface ScreeningResponse {
  hasResults?: boolean;
  job: ScreeningJob | null;
  candidates: Candidate[];
  duplicates: { fileA: string; fileB: string; similarity: number }[];
  stats: DashboardStats;
}

export interface AuthUser {
  id: number;
  fullName: string;
  email: string;
  phone: string;
}

const API_BASE = "/api";

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map((d: { msg?: string }) => d.msg).join(", ");
  } catch {
    /* fall through */
  }
  return `Request failed (${response.status})`;
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function loginUser(email: string, password: string): Promise<{ token: string; user: AuthUser }> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json();
}

export async function registerUser(
  fullName: string,
  email: string,
  password: string,
  phone = ""
): Promise<string> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name: fullName, email, password, phone }),
  });
  if (!response.ok) throw new Error(await parseError(response));
  const data = await response.json();
  return data.message as string;
}

export async function fetchCurrentUser(token: string): Promise<AuthUser> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error(await parseError(response));
  const data = await response.json();
  return data.user as AuthUser;
}

export async function logoutUser(token: string): Promise<void> {
  await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function updateProfile(token: string, fullName: string, phone: string): Promise<AuthUser> {
  const response = await fetch(`${API_BASE}/auth/profile`, {
    method: "PUT",
    headers: { ...authHeaders(token), "Content-Type": "application/json" },
    body: JSON.stringify({ full_name: fullName, phone }),
  });
  if (!response.ok) throw new Error(await parseError(response));
  const data = await response.json();
  return data.user as AuthUser;
}

export async function fetchUserDashboard(token: string): Promise<ScreeningResponse> {
  const response = await fetch(`${API_BASE}/dashboard`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json();
}

export async function runScreening(
  jobDescription: string,
  files: File[],
  token?: string | null
): Promise<ScreeningResponse> {
  const formData = new FormData();
  formData.append("job_description", jobDescription);
  files.forEach((file) => formData.append("resumes", file));

  const headers: HeadersInit = {};
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}/screen`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  const data = await response.json();
  return { ...data, hasResults: true, job: data.job ?? null };
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
