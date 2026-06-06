import { useState } from "react";
import { motion } from "framer-motion";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScoreGauge } from "@/components/ats/ScoreGauge";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useScreening } from "@/contexts/ScreeningContext";

export function ATSScoring() {
  const { candidates, hasResults, isLoadingDashboard } = useScreening();
  const [selectedId, setSelectedId] = useState(candidates[0]?.id ?? "");

  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">ATS Scoring Engine</h1>
          <p className="text-muted-foreground">Loading scores...</p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">ATS Scoring Engine</h1>
          <p className="text-muted-foreground">Run AI screening to see scores</p>
        </div>
        <EmptyState />
      </div>
    );
  }

  const candidate = candidates.find((c) => c.id === selectedId) ?? candidates[0];
  const chartData = [
    { name: "Skills", score: candidate.scoreBreakdown.skills },
    { name: "Experience", score: candidate.scoreBreakdown.experience },
    { name: "Education", score: candidate.scoreBreakdown.education },
    { name: "Certs", score: candidate.scoreBreakdown.certifications },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">ATS Scoring Engine</h1>
        <p className="text-muted-foreground">Weighted: Skills 50% · Experience 20% · Education 15% · Certs 15%</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {candidates.map((c) => (
          <button
            type="button"
            key={c.id}
            onClick={() => setSelectedId(c.id)}
            className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
              selectedId === c.id ? "border-primary bg-primary/10 text-primary" : "hover:bg-accent"
            }`}
          >
            {c.name} ({c.atsScore})
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="flex items-center justify-center p-8">
          <ScoreGauge score={candidate.atsScore} size={200} />
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Score Breakdown — {candidate.name}</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>All Candidates — ATS Ranking</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {candidates.map((c, i) => (
              <motion.div key={c.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-center gap-4">
                <span className="w-8 text-sm font-bold text-muted-foreground">#{c.rank}</span>
                <span className="w-32 text-sm font-medium truncate">{c.name}</span>
                <div className="flex-1 h-3 rounded-full bg-secondary overflow-hidden">
                  <motion.div className="h-full rounded-full bg-primary" initial={{ width: 0 }} animate={{ width: `${c.atsScore}%` }} transition={{ duration: 0.8, delay: i * 0.1 }} />
                </div>
                <span className="w-12 text-sm font-bold text-right">{c.atsScore}</span>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
