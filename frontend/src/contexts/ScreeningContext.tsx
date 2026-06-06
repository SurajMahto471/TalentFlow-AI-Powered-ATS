import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import type { Candidate, DashboardStats } from "@/types";
import {
  fetchUserDashboard,
  runScreening,
  type ScreeningJob,
  type ScreeningResponse,
} from "@/services/api";
import { getAuthToken, useAuth } from "@/contexts/AuthContext";

const emptyStats: DashboardStats = {
  totalApplications: 0,
  shortlisted: 0,
  rejected: 0,
  avgAtsScore: 0,
  activeJobs: 0,
  applicationsGrowth: 0,
  shortlistedGrowth: 0,
  rejectedGrowth: 0,
  scoreGrowth: 0,
};

interface ScreeningContextType {
  job: ScreeningJob | null;
  candidates: Candidate[];
  stats: DashboardStats;
  duplicates: ScreeningResponse["duplicates"];
  isScreening: boolean;
  isLoadingDashboard: boolean;
  error: string | null;
  hasResults: boolean;
  scopedUserId: number | null;
  runAIScreening: (jobDescription: string, files: File[]) => Promise<void>;
  clearResults: () => void;
  getCandidate: (id: string) => Candidate | undefined;
}

const ScreeningContext = createContext<ScreeningContextType | undefined>(undefined);

export function ScreeningProvider({ children }: { children: ReactNode }) {
  const { user, isLoading: authLoading } = useAuth();
  const [job, setJob] = useState<ScreeningJob | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [stats, setStats] = useState<DashboardStats>(emptyStats);
  const [duplicates, setDuplicates] = useState<ScreeningResponse["duplicates"]>([]);
  const [isScreening, setIsScreening] = useState(false);
  const [isLoadingDashboard, setIsLoadingDashboard] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scopedUserId, setScopedUserId] = useState<number | null>(null);
  const fetchGeneration = useRef(0);

  const clearResults = useCallback(() => {
    setJob(null);
    setCandidates([]);
    setStats(emptyStats);
    setDuplicates([]);
    setError(null);
    setScopedUserId(null);
  }, []);

  const applyDashboardData = useCallback((data: ScreeningResponse, userId: number) => {
    if (data.hasResults && data.candidates.length > 0) {
      setJob(data.job);
      setCandidates(data.candidates);
      setStats(data.stats);
      setDuplicates(data.duplicates);
    } else {
      setJob(null);
      setCandidates([]);
      setStats(emptyStats);
      setDuplicates([]);
    }
    setScopedUserId(userId);
  }, []);

  const loadUserDashboard = useCallback(async (userId: number) => {
    const token = getAuthToken();
    if (!token) {
      clearResults();
      return;
    }

    const generation = ++fetchGeneration.current;
    setIsLoadingDashboard(true);
    setError(null);
    clearResults();

    try {
      const data = await fetchUserDashboard(token);
      if (generation !== fetchGeneration.current) return;
      applyDashboardData(data, userId);
    } catch (err) {
      if (generation !== fetchGeneration.current) return;
      setError(err instanceof Error ? err.message : "Failed to load dashboard data");
      clearResults();
    } finally {
      if (generation === fetchGeneration.current) {
        setIsLoadingDashboard(false);
      }
    }
  }, [applyDashboardData, clearResults]);

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      fetchGeneration.current += 1;
      clearResults();
      setIsLoadingDashboard(false);
      return;
    }

    loadUserDashboard(user.id);
  }, [user?.id, authLoading, loadUserDashboard, clearResults]);

  const runAIScreening = async (jobDescription: string, files: File[]) => {
    const token = getAuthToken();
    const userId = user?.id;
    if (!token || !userId) {
      throw new Error("You must be logged in to run screening.");
    }

    setIsScreening(true);
    setError(null);
    try {
      const result = await runScreening(jobDescription, files, token);
      if (user?.id !== userId) return;
      applyDashboardData({ ...result, hasResults: true }, userId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Screening failed. Is the API running on port 8000?");
      throw err;
    } finally {
      setIsScreening(false);
    }
  };

  const getCandidate = (id: string) => {
    if (scopedUserId !== user?.id) return undefined;
    return candidates.find((c) => c.id === id);
  };

  return (
    <ScreeningContext.Provider
      value={{
        job,
        candidates,
        stats,
        duplicates,
        isScreening,
        isLoadingDashboard,
        error,
        hasResults: scopedUserId === user?.id && candidates.length > 0,
        scopedUserId,
        runAIScreening,
        clearResults,
        getCandidate,
      }}
    >
      {children}
    </ScreeningContext.Provider>
  );
}

export function useScreening() {
  const ctx = useContext(ScreeningContext);
  if (!ctx) throw new Error("useScreening must be used within ScreeningProvider");
  return ctx;
}
