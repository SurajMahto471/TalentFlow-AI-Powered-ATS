import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useScreening } from "@/contexts/ScreeningContext";

export function Jobs() {
  const { job, candidates, hasResults, isLoadingDashboard } = useScreening();

  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Job Descriptions</h1>
          <p className="text-muted-foreground">Loading your jobs...</p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (!hasResults || !job) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Job Descriptions</h1>
          <p className="text-muted-foreground">Job details appear after you run AI screening</p>
        </div>
        <EmptyState title="No job description yet" description="Paste a job description in AI Screening to analyze candidates against it." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Job Descriptions</h1>
        <p className="text-muted-foreground">Current active screening job</p>
      </div>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <CardTitle>{job.title}</CardTitle>
            <Badge variant="success">Active</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium mb-2">Required Skills</p>
            <div className="flex flex-wrap gap-1">
              {job.requiredSkills.map((s) => (
                <Badge key={s} variant="outline">{s}</Badge>
              ))}
            </div>
          </div>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <span>{job.experienceRequired}+ years experience required</span>
            <span>{candidates.length} applicants screened</span>
          </div>
          <div>
            <p className="text-sm font-medium mb-2">Full Description</p>
            <div className="rounded-lg bg-secondary/50 p-4 text-sm whitespace-pre-wrap max-h-48 overflow-y-auto">
              {job.rawText}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
