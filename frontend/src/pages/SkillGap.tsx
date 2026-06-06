import { useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Check, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useScreening } from "@/contexts/ScreeningContext";

export function SkillGap() {
  const { candidates, job, hasResults, isLoadingDashboard } = useScreening();
  const [selectedId, setSelectedId] = useState(candidates[0]?.id ?? "");

  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Skill Gap Analysis</h1>
          <p className="text-muted-foreground">Loading your skill gap data...</p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (!hasResults || !job) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Skill Gap Analysis</h1>
          <p className="text-muted-foreground">Run AI screening to compare skills</p>
        </div>
        <EmptyState />
      </div>
    );
  }

  const candidate = candidates.find((c) => c.id === selectedId) ?? candidates[0];
  const requiredSkills = job.requiredSkills;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Skill Gap Analysis</h1>
        <p className="text-muted-foreground">Required: {requiredSkills.join(", ") || "None detected"}</p>
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
            {c.name}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Required Skills vs Candidate</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {requiredSkills.length === 0 ? (
              <p className="text-sm text-muted-foreground">No skills extracted from job description</p>
            ) : (
              requiredSkills.map((skill, i) => {
                const has = candidate.matchedSkills.some((s) => s.toLowerCase() === skill.toLowerCase());
                return (
                  <motion.div key={skill} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-center gap-3">
                    {has ? <Check className="h-5 w-5 text-emerald-500 shrink-0" /> : <X className="h-5 w-5 text-red-500 shrink-0" />}
                    <span className="flex-1 text-sm font-medium">{skill}</span>
                    <Progress value={has ? 100 : 0} className="w-24 h-2" />
                  </motion.div>
                );
              })
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle className="text-emerald-600">Matched Skills</CardTitle></CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {candidate.matchedSkills.map((s) => <Badge key={s} variant="success">{s}</Badge>)}
                {candidate.matchedSkills.length === 0 && <p className="text-sm text-muted-foreground">No matches</p>}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-red-500">Missing Skills</CardTitle></CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {candidate.missingSkills.map((s) => <Badge key={s} variant="danger">{s}</Badge>)}
                {candidate.missingSkills.length === 0 && <p className="text-sm text-muted-foreground">Full match!</p>}
              </div>
            </CardContent>
          </Card>
          {candidate.missingSkills.length > 0 && (
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <BookOpen className="h-5 w-5" />
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {candidate.missingSkills.map((s) => (
                  <p key={s} className="text-sm text-muted-foreground">Learn <span className="font-medium text-foreground">{s}</span> through hands-on projects</p>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
