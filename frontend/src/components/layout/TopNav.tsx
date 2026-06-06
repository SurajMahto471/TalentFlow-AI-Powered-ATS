import { useNavigate } from "react-router-dom";
import { Bell, LogOut, Menu, Moon, Search, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { useTheme } from "@/contexts/ThemeContext";
import { useAuth } from "@/contexts/AuthContext";

interface TopNavProps {
  onMenuClick?: () => void;
}

export function TopNav({ onMenuClick }: TopNavProps) {
  const navigate = useNavigate();
  const { darkMode, toggleDarkMode } = useTheme();
  const { user, logout } = useAuth();

  const initials = user?.fullName
    ? user.fullName.split(" ").slice(0, 2).map((w) => w[0]).join("").toUpperCase()
    : "U";

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-card/80 px-4 backdrop-blur-md lg:px-8">
      <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenuClick}>
        <Menu className="h-5 w-5" />
      </Button>

      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search candidates, skills, jobs..." className="pl-10 bg-secondary/50 border-0" />
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden items-center gap-2 sm:flex">
          {darkMode ? <Moon className="h-4 w-4 text-muted-foreground" /> : <Sun className="h-4 w-4 text-muted-foreground" />}
          <Switch checked={darkMode} onCheckedChange={toggleDarkMode} />
        </div>

        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-danger" />
        </Button>

        <button
          type="button"
          onClick={() => navigate("/settings")}
          className="flex items-center gap-3 rounded-lg border px-3 py-1.5 transition-colors hover:bg-accent cursor-pointer"
        >
          <Avatar className="h-8 w-8">
            <AvatarFallback className="text-xs">{initials}</AvatarFallback>
          </Avatar>
          <div className="hidden sm:block text-left">
            <p className="text-sm font-medium leading-none">{user?.fullName ?? "User"}</p>
            <p className="text-xs text-muted-foreground">{user?.email ?? ""}</p>
          </div>
        </button>

        <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
          <LogOut className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
