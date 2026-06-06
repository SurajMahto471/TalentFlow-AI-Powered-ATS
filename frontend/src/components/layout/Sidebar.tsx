import { NavLink } from "react-router-dom";
import {
  BarChart3,
  Brain,
  Briefcase,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Settings,
  Target,
  Users,
  X,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/candidates", icon: Users, label: "Candidates" },
  { to: "/jobs", icon: Briefcase, label: "Job Descriptions" },
  { to: "/scoring", icon: Target, label: "ATS Scoring" },
  { to: "/skill-gap", icon: Brain, label: "Skill Gap Analysis" },
  { to: "/interview", icon: MessageSquare, label: "Interview Questions" },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/upload", icon: FileText, label: "AI Screening" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

interface SidebarProps {
  mobileOpen?: boolean;
  onClose?: () => void;
}

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex-1 space-y-1 overflow-y-auto p-4">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors cursor-pointer",
              isActive
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-accent hover:text-foreground"
            )
          }
        >
          <item.icon className="h-[18px] w-[18px] shrink-0" />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

export function Sidebar({ mobileOpen = false, onClose }: SidebarProps) {
  return (
    <>
      {/* Desktop sidebar */}
      <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r bg-card lg:flex">
        <div className="flex h-16 items-center gap-3 border-b px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
            <Zap className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">TalentFlow</h1>
            <p className="text-xs text-muted-foreground">AI-Powered ATS</p>
          </div>
        </div>
        <NavItems />
        <div className="border-t p-4">
          <div className="rounded-lg bg-primary/5 p-4">
            <p className="text-xs font-semibold text-primary">Pro Plan</p>
            <p className="mt-1 text-xs text-muted-foreground">Unlimited screenings & analytics</p>
          </div>
        </div>
      </aside>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={onClose}
            aria-hidden="true"
          />
          <aside className="absolute left-0 top-0 flex h-full w-72 flex-col bg-card shadow-elevated">
            <div className="flex h-16 items-center justify-between border-b px-4">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                  <Zap className="h-5 w-5 text-primary-foreground" />
                </div>
                <h1 className="text-lg font-bold">TalentFlow</h1>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <NavItems onNavigate={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
