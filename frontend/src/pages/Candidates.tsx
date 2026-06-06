import { CandidateTable } from "@/components/dashboard/CandidateTable";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useScreening } from "@/contexts/ScreeningContext";

export function Candidates() {
  const { candidates, hasResults, isLoadingDashboard } = useScreening();

  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Candidates</h1>
          <p className="text-muted-foreground">Loading your candidates...</p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Candidates</h1>
          <p className="text-muted-foreground">No candidates screened yet</p>
        </div>
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Candidates</h1>
        <p className="text-muted-foreground">{candidates.length} candidates ranked by ATS score</p>
      </div>
      <CandidateTable data={candidates} />
    </div>
  );
}
