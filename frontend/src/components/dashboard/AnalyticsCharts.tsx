import {
  Bar, BarChart, CartesianGrid, Cell, Funnel, FunnelChart, LabelList,
  Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useScreening } from "@/contexts/ScreeningContext";

const COLORS = ["#3b82f6", "#60a5fa", "#93c5fd", "#2563eb", "#1d4ed8"];

function buildScoreDistribution(scores: number[]) {
  const buckets = [
    { range: "0-20", min: 0, max: 20, count: 0 },
    { range: "21-40", min: 21, max: 40, count: 0 },
    { range: "41-60", min: 41, max: 60, count: 0 },
    { range: "61-80", min: 61, max: 80, count: 0 },
    { range: "81-100", min: 81, max: 100, count: 0 },
  ];
  scores.forEach((s) => {
    const bucket = buckets.find((b) => s >= b.min && s <= b.max);
    if (bucket) bucket.count++;
  });
  return buckets.map(({ range, count }) => ({ range, count }));
}

function buildSkillDemand(candidates: { skills: string[] }[]) {
  const counts: Record<string, number> = {};
  candidates.forEach((c) => c.skills.forEach((s) => { counts[s] = (counts[s] || 0) + 1; }));
  return Object.entries(counts)
    .map(([skill, count]) => ({ skill, demand: count * 10 }))
    .sort((a, b) => b.demand - a.demand)
    .slice(0, 6);
}

function buildExperienceDist(candidates: { experience: number }[]) {
  const buckets = [
    { years: "0-1", count: 0 },
    { years: "1-3", count: 0 },
    { years: "3-5", count: 0 },
    { years: "5-8", count: 0 },
    { years: "8+", count: 0 },
  ];
  candidates.forEach((c) => {
    const y = c.experience;
    if (y <= 1) buckets[0].count++;
    else if (y <= 3) buckets[1].count++;
    else if (y <= 5) buckets[2].count++;
    else if (y <= 8) buckets[3].count++;
    else buckets[4].count++;
  });
  return buckets;
}

function buildFunnel(total: number, shortlisted: number, interview: number) {
  return [
    { stage: "Applied", count: total },
    { stage: "Screened", count: total },
    { stage: "Shortlisted", count: shortlisted },
    { stage: "Interview", count: interview },
    { stage: "Offer", count: Math.max(1, Math.floor(shortlisted * 0.2)) },
  ];
}

export function AnalyticsCharts() {
  const { candidates, stats } = useScreening();
  const scores = candidates.map((c) => c.atsScore);
  const interviewCount = candidates.filter((c) => c.status === "Interview" || c.status === "Shortlisted").length;

  const atsScoreDistribution = buildScoreDistribution(scores);
  const skillDemand = buildSkillDemand(candidates);
  const experienceDistribution = buildExperienceDist(candidates);
  const hiringFunnel = buildFunnel(stats.totalApplications, stats.shortlisted, interviewCount);

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader><CardTitle className="text-base">ATS Score Distribution</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={atsScoreDistribution}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {atsScoreDistribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Skill Frequency</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={skillDemand} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis dataKey="skill" type="category" width={70} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="demand" fill="#3b82f6" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Experience Distribution</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={experienceDistribution}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="years" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Hiring Funnel</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <FunnelChart>
              <Tooltip />
              <Funnel dataKey="count" data={hiringFunnel} isAnimationActive>
                {hiringFunnel.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                <LabelList position="right" fill="hsl(var(--foreground))" stroke="none" dataKey="stage" />
              </Funnel>
            </FunnelChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
