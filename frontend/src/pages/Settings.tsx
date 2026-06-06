import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { useTheme } from "@/contexts/ThemeContext";
import { useAuth } from "@/contexts/AuthContext";

export function Settings() {
  const { darkMode, toggleDarkMode } = useTheme();
  const { user, updateUserProfile, logout } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (user) {
      setFullName(user.fullName);
      setPhone(user.phone);
    }
  }, [user]);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await updateUserProfile(fullName, phone);
      setMessage("Profile updated successfully.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your account and preferences</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Full Name</label>
            <Input value={fullName} onChange={(e) => setFullName(e.target.value)} className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">Email</label>
            <Input value={user?.email ?? ""} disabled className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">Phone</label>
            <Input value={phone} onChange={(e) => setPhone(e.target.value)} className="mt-1" />
          </div>
          {message && <p className="text-sm text-muted-foreground">{message}</p>}
          <div className="flex gap-2">
            <Button onClick={handleSave} disabled={saving}>Save Changes</Button>
            <Button variant="outline" onClick={handleLogout}>Logout</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Appearance</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Dark Mode</p>
            <p className="text-xs text-muted-foreground">Toggle between light and dark themes</p>
          </div>
          <Switch checked={darkMode} onCheckedChange={toggleDarkMode} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {["New applications", "Shortlist alerts", "Weekly reports"].map((n) => (
            <div key={n} className="flex items-center justify-between">
              <span className="text-sm">{n}</span>
              <Switch defaultChecked />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
