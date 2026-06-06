import { AnalyticsCharts } from "@/components/dashboard/AnalyticsCharts";
import { CandidateTable } from "@/components/dashboard/CandidateTable";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useScreening } from "@/contexts/ScreeningContext";

export function Analytics() {
  const { candidates, hasResults, isLoadingDashboard } = useScreening();

  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Hiring Analytics</h1>
          <p className="text-muted-foreground">Loading your analytics...</p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Hiring Analytics</h1>
          <p className="text-muted-foreground">Analytics appear after you run AI screening</p>
        </div>
        <AnalyticsCharts />
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Hiring Analytics</h1>
        <p className="text-muted-foreground">Insights from your latest screening run</p>
      </div>
      <AnalyticsCharts />
      <CandidateTable data={candidates} showFilters={false} />
    </div>
  );
}
