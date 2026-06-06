import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { ScreeningProvider } from "@/contexts/ScreeningContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { MainLayout } from "@/components/layout/MainLayout";
import { Login } from "@/pages/Login";
import { Dashboard } from "@/pages/Dashboard";
import { Candidates } from "@/pages/Candidates";
import { CandidateDetail } from "@/pages/CandidateDetail";
import { Jobs } from "@/pages/Jobs";
import { ATSScoring } from "@/pages/ATSScoring";
import { SkillGap } from "@/pages/SkillGap";
import { InterviewQuestions } from "@/pages/InterviewQuestions";
import { Analytics } from "@/pages/Analytics";
import { ResumeUpload } from "@/pages/ResumeUpload";
import { Settings } from "@/pages/Settings";

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ScreeningProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route element={<ProtectedRoute />}>
                <Route element={<MainLayout />}>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/candidates" element={<Candidates />} />
                  <Route path="/candidates/:id" element={<CandidateDetail />} />
                  <Route path="/jobs" element={<Jobs />} />
                  <Route path="/scoring" element={<ATSScoring />} />
                  <Route path="/skill-gap" element={<SkillGap />} />
                  <Route path="/interview" element={<InterviewQuestions />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/upload" element={<ResumeUpload />} />
                  <Route path="/settings" element={<Settings />} />
                </Route>
              </Route>
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </BrowserRouter>
        </ScreeningProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
