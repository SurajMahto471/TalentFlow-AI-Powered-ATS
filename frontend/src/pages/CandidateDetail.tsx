import { Link, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Award, Briefcase, GraduationCap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScoreGauge } from "@/components/ats/ScoreGauge";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { useScreening } from "@/contexts/ScreeningContext";
import { cn, getScoreColor } from "@/lib/utils";

export function CandidateDetail() {
  const { id } = useParams();
  const { getCandidate, isLoadingDashboard } = useScreening();
  const candidate = id ? getCandidate(id) : undefined;

  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <DashboardSkeleton />
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Candidate not found. Run AI screening first.</p>
        <Button asChild className="mt-4"><Link to="/upload">Run AI Screening</Link></Button>
      </div>
    );
  }

  const breakdown = candidate.scoreBreakdown;

  return (
    <div className="space-y-6">
      <Button variant="ghost" asChild>
        <Link to="/candidates"><ArrowLeft className="h-4 w-4 mr-2" /> Back</Link>
      </Button>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardContent className="flex flex-col items-center p-8">
            <Avatar className="h-24 w-24 mb-4">
              <AvatarFallback className="text-2xl">{candidate.avatar}</AvatarFallback>
            </Avatar>
            <h2 className="text-xl font-bold">{candidate.name}</h2>
            <p className="text-sm text-muted-foreground">{candidate.company || candidate.email}</p>
            <Badge className="mt-2" variant={candidate.verdict === "Strong Match" || candidate.verdict === "Good Match" ? "success" : "secondary"}>
              {candidate.verdict}
            </Badge>
            <div className="mt-6">
              <ScoreGauge score={candidate.atsScore} size={160} />
            </div>
            <p className="mt-4 text-center text-sm text-muted-foreground">{candidate.recommendation}</p>
          </CardContent>
        </Card>

        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader><CardTitle>ATS Score Breakdown</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {[
                { label: "Skills", value: breakdown.skills, weight: "50%" },
                { label: "Experience", value: breakdown.experience, weight: "20%" },
                { label: "Education", value: breakdown.education, weight: "15%" },
                { label: "Certifications", value: breakdown.certifications, weight: "15%" },
              ].map((item, i) => (
                <motion.div key={item.label} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">{item.label} <span className="text-muted-foreground">({item.weight})</span></span>
                    <span className={cn("font-bold", getScoreColor(item.value))}>{item.value}%</span>
                  </div>
                  <Progress value={item.value} className="h-2" />
                </motion.div>
              ))}
            </CardContent>
          </Card>

          <div className="grid gap-6 sm:grid-cols-2">
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <Briefcase className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">Experience</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{candidate.experience} years</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <GraduationCap className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">Education</CardTitle>
              </CardHeader>
              <CardContent>
                {candidate.education.length > 0
                  ? candidate.education.map((e) => <p key={e} className="text-sm">{e}</p>)
                  : <p className="text-sm text-muted-foreground">Not detected</p>}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader><CardTitle>Skills</CardTitle></CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {candidate.skills.map((s) => (
                  <Badge key={s} variant={candidate.matchedSkills.includes(s) ? "success" : "secondary"}>{s}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {candidate.certifications.length > 0 && (
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <Award className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">Certifications</CardTitle>
              </CardHeader>
              <CardContent>
                {candidate.certifications.map((c) => <Badge key={c} variant="outline" className="mr-2">{c}</Badge>)}
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader><CardTitle>Resume</CardTitle></CardHeader>
            <CardContent>
              <div className="rounded-lg bg-secondary/50 p-4 text-sm leading-relaxed whitespace-pre-wrap max-h-64 overflow-y-auto">
                {candidate.resumeText || "No text extracted"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Screening Reasoning</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {candidate.reasoning.map((r) => (
                  <li key={r} className="flex items-start gap-2 text-sm">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                    {r}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
