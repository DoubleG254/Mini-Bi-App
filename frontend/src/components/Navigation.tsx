import { A, useLocation, useNavigate } from "@solidjs/router";
import { createSignal, Show } from "solid-js";
import { ChartBarIcon, Upload, History, LogOut } from "lucide-solid";
import { logoutSession } from "../lib/api";

export function Navigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const [logoutError, setLogoutError] = createSignal<string | null>(null);

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const navClass = (path: string) => {
    if (isActive(path)) {
      return "bg-accent text-accent-foreground";
    }

    return "text-muted-foreground hover:text-foreground";
  };

  const handleLogout = async () => {
    try {
      await logoutSession();
    } catch (error) {
      setLogoutError(error instanceof Error ? error.message : "Unable to sign out");
    } finally {
      navigate("/", { replace: true });
    }
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
                class={`px-4 py-2 rounded-lg transition-colors ${navClass("/dashboard")}`}
              >
                Dashboard
              </A>
              <A
                href="/upload"
                class={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${navClass("/upload")}`}
              >
                <Upload class="w-4 h-4" />
                Upload
              </A>
              <A
                href="/history"
                class={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${navClass("/history")}`}
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
        <Show when={logoutError()}>
          <p class="mt-3 text-sm text-red-500">{logoutError()}</p>
        </Show>
      </div>
    </nav>
  );
}
