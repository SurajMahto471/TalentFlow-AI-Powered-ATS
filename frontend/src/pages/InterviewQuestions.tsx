import { useState } from "react";
import { motion } from "framer-motion";
import { Copy, Download, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useScreening } from "@/contexts/ScreeningContext";

const categoryColors: Record<string, string> = {
  Technical: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  Behavioral: "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400",
  "Domain Specific": "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
};

function categorizeQuestion(q: string, index: number): string {
  const lower = q.toLowerCase();
  if (lower.includes("experience") || lower.includes("team") || lower.includes("deadline") || lower.includes("stakeholder")) {
    return "Behavioral";
  }
  if (lower.includes("deploy") || lower.includes("docker") || lower.includes("django") || lower.includes("sql")) {
    return "Domain Specific";
  }
  return index % 3 === 0 ? "Technical" : index % 3 === 1 ? "Domain Specific" : "Behavioral";
}

export function InterviewQuestions() {
  const { candidates, hasResults, isLoadingDashboard } = useScreening();
  const [selectedId, setSelectedId] = useState(candidates[0]?.id ?? "");
  const [copied, setCopied] = useState<number | null>(null);

  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Interview Questions</h1>
          <p className="text-muted-foreground">Loading questions...</p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Interview Questions</h1>
          <p className="text-muted-foreground">Questions are generated after AI screening</p>
        </div>
        <EmptyState />
      </div>
    );
  }

  const candidate = candidates.find((c) => c.id === selectedId) ?? candidates[0];
  const questions = candidate.interviewQuestions ?? [];

  const handleCopy = (index: number, text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(index);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleDownload = () => {
    const text = questions.map((q, i) => `${i + 1}. ${q}`).join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `interview-${candidate.name.replace(/\s/g, "-")}.txt`;
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Interview Questions</h1>
          <p className="text-muted-foreground">AI-generated for {candidate.name}</p>
        </div>
        {questions.length > 0 && (
          <Button variant="outline" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" /> Download
          </Button>
        )}
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

      {questions.length === 0 ? (
        <p className="text-sm text-muted-foreground">No questions generated for this candidate.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {questions.map((q, i) => {
            const category = categorizeQuestion(q, i);
            return (
              <motion.div key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                <Card className="group hover:shadow-elevated transition-all">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-3">
                        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${categoryColors[category]}`}>
                          {category}
                        </span>
                        <p className="text-sm leading-relaxed">{q}</p>
                      </div>
                      <Button variant="ghost" size="icon" className="shrink-0" onClick={() => handleCopy(i, q)}>
                        {copied === i ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
