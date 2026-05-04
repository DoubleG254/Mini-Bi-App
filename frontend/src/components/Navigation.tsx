import { A, useLocation, useNavigate } from "@solidjs/router";
import { ChartBarIcon, Upload, History, LogOut } from "lucide-solid";

export function Navigation() {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  // Call server api
  const handleLogout = () => {
    navigate("/");
  };

  return (
    <nav class="border-b border-border bg-background">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-8">
            <A href="/dashboard" class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <ChartBarIcon class="w-5 h-5 text-primary-foreground" />
              </div>
              <span class="text-xl tracking-tight">DataInsight</span>
            </A>

            <div class="flex items-center gap-1">
              <A
                href="/dashboard"
                class={`px-4 py-2 rounded-lg transition-colors ${isActive("/dashboard")
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                Dashboard
              </A>
              <A
                href="/upload"
                class={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${isActive("/upload")
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                <Upload class="w-4 h-4" />
                Upload
              </A>
              <A
                href="/history"
                class={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${isActive("/history")
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                <History class="w-4 h-4" />
                History
              </A>
            </div>
          </div>

          <button
            onClick={handleLogout}
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-muted-foreground hover:text-foreground transition-colors"
          >
            <LogOut class="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </div>
    </nav>
  );
}
