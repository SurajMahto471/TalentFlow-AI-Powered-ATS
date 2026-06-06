import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, Eye, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { Candidate } from "@/types";
import { cn, getScoreColor, getStatusColor } from "@/lib/utils";

interface CandidateTableProps {
  data: Candidate[];
  showFilters?: boolean;
}

type SortField = "atsScore" | "skillMatch" | "qualityScore" | "experience";

const SORT_OPTIONS: { value: SortField; label: string }[] = [
  { value: "atsScore", label: "ATS Score" },
  { value: "skillMatch", label: "Skill Match" },
  { value: "qualityScore", label: "Quality Score" },
  { value: "experience", label: "Experience" },
];

const PAGE_SIZE = 5;

function getSortValue(candidate: Candidate, field: SortField): number {
  switch (field) {
    case "atsScore":
      return candidate.atsScore;
    case "skillMatch":
      return candidate.skillMatch ?? candidate.matchPercentage;
    case "qualityScore":
      return candidate.qualityScore ?? 0;
    case "experience":
      return candidate.experience;
    default:
      return 0;
  }
}

export function CandidateTable({ data, showFilters = true }: CandidateTableProps) {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [sortBy, setSortBy] = useState<SortField>("atsScore");
  const [page, setPage] = useState(0);

  const statuses = ["All", "Shortlisted", "Interview", "Review", "Rejected"];

  let filtered = data.filter((c) => {
    const matchSearch =
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.skills.some((s) => s.toLowerCase().includes(search.toLowerCase()));
    const matchStatus = statusFilter === "All" || c.status === statusFilter;
    return matchSearch && matchStatus;
  });

  filtered = [...filtered].sort((a, b) => getSortValue(b, sortBy) - getSortValue(a, sortBy));
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  return (
    <Card>
      <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <CardTitle>Candidate Rankings</CardTitle>
        {showFilters && (
          <div className="flex flex-wrap gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search..."
                className="w-48 pl-8"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              />
            </div>
            <select
              className="h-10 rounded-lg border border-input bg-background px-3 text-sm"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            >
              {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <select
              className="h-10 rounded-lg border border-input bg-background px-3 text-sm"
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value as SortField); setPage(0); }}
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-muted-foreground">
                <th className="pb-3 pr-4 font-medium">Rank</th>
                <th className="pb-3 pr-4 font-medium">Candidate</th>
                <th className="pb-3 pr-4 font-medium">ATS Score</th>
                <th className="pb-3 pr-4 font-medium hidden sm:table-cell">Skill Match</th>
                <th className="pb-3 pr-4 font-medium hidden md:table-cell">Quality</th>
                <th className="pb-3 pr-4 font-medium hidden md:table-cell">Experience</th>
                <th className="pb-3 pr-4 font-medium hidden lg:table-cell">Skills</th>
                <th className="pb-3 pr-4 font-medium">Status</th>
                <th className="pb-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((c, i) => (
                <motion.tr
                  key={c.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className="border-b last:border-0 hover:bg-accent/50 transition-colors"
                >
                  <td className="py-4 pr-4 font-semibold text-muted-foreground">
                    #{page * PAGE_SIZE + i + 1}
                  </td>
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-9 w-9">
                        <AvatarFallback>{c.avatar}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{c.name}</p>
                        <p className="text-xs text-muted-foreground">{c.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className={cn("py-4 pr-4 font-bold", getScoreColor(c.atsScore))}>{c.atsScore}</td>
                  <td className="py-4 pr-4 hidden sm:table-cell font-medium">
                    {(c.skillMatch ?? c.matchPercentage).toFixed(1)}%
                  </td>
                  <td className="py-4 pr-4 hidden md:table-cell">{(c.qualityScore ?? 0).toFixed(0)}</td>
                  <td className="py-4 pr-4 hidden md:table-cell">{c.experience} yrs</td>
                  <td className="py-4 pr-4 hidden lg:table-cell">
                    <div className="flex flex-wrap gap-1 max-w-[200px]">
                      {c.skills.slice(0, 3).map((s) => (
                        <Badge key={s} variant="secondary" className="text-[10px]">{s}</Badge>
                      ))}
                      {c.skills.length > 3 && (
                        <Badge variant="outline" className="text-[10px]">+{c.skills.length - 3}</Badge>
                      )}
                    </div>
                  </td>
                  <td className="py-4 pr-4">
                    <span className={cn("inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold", getStatusColor(c.status))}>
                      {c.status}
                    </span>
                  </td>
                  <td className="py-4">
                    <Button variant="ghost" size="sm" onClick={() => navigate(`/candidates/${c.id}`)}>
                      <Eye className="h-4 w-4 mr-1" /> View
                    </Button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, filtered.length)} of {filtered.length}
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(page - 1)}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
