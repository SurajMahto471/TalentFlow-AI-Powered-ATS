import { Briefcase, TrendingUp, UserCheck, Users, XCircle } from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
import { AnalyticsCharts } from "@/components/dashboard/AnalyticsCharts";
import { CandidateTable } from "@/components/dashboard/CandidateTable";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useScreening } from "@/contexts/ScreeningContext";

export function Dashboard() {
  const { stats, candidates, hasResults, job, isLoadingDashboard } = useScreening();

  if (isLoadingDashboard) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Recruiter Dashboard</h1>
          <p className="text-muted-foreground">Loading your screening data...</p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (!hasResults) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Recruiter Dashboard</h1>
          <p className="text-muted-foreground">Your personal screening workspace — data is isolated to your account</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <StatCard title="Total Candidates" value={0} growth={0} icon={Users} delay={0} />
          <StatCard title="Shortlisted" value={0} growth={0} icon={UserCheck} iconColor="text-emerald-500" delay={0.1} />
          <StatCard title="Rejected" value={0} growth={0} icon={XCircle} iconColor="text-red-500" delay={0.2} />
          <StatCard title="Avg ATS Score" value="0%" growth={0} icon={TrendingUp} iconColor="text-blue-500" delay={0.3} />
          <StatCard title="Active Jobs" value={0} growth={0} icon={Briefcase} iconColor="text-violet-500" delay={0.4} />
        </div>

        <AnalyticsCharts />
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Recruiter Dashboard</h1>
        <p className="text-muted-foreground">
          Results for <span className="font-medium text-foreground">{job?.title}</span>
          {" "}— {candidates.length} candidate{candidates.length !== 1 ? "s" : ""} screened
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard title="Total Applications" value={stats.totalApplications} growth={0} icon={Users} delay={0} />
        <StatCard title="Shortlisted" value={stats.shortlisted} growth={0} icon={UserCheck} iconColor="text-emerald-500" delay={0.1} />
        <StatCard title="Rejected" value={stats.rejected} growth={0} icon={XCircle} iconColor="text-red-500" delay={0.2} />
        <StatCard title="Avg ATS Score" value={`${stats.avgAtsScore}%`} growth={0} icon={TrendingUp} iconColor="text-blue-500" delay={0.3} />
        <StatCard title="Active Jobs" value={stats.activeJobs} growth={0} icon={Briefcase} iconColor="text-violet-500" delay={0.4} />
      </div>

      <AnalyticsCharts />
      <CandidateTable data={candidates} />
    </div>
  );
}
