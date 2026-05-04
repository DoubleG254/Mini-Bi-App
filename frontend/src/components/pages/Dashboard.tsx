import { createAsync, query } from "@solidjs/router";
import { For, Show } from "solid-js";
import { Navigation } from "../Navigation";
import { TrendingUp, Database, FileText, Activity } from "lucide-solid";
import { A } from "@solidjs/router";
import { fetchCurrentUser, fetchDatasets, fetchReports } from "../../lib/api";

export default function DashboardPage() {
  const profileQuery = query(async () => fetchCurrentUser(), "dashboard-profile");
  const datasetsQuery = query(async () => fetchDatasets(), "dashboard-datasets");
  const reportsQuery = query(async () => fetchReports(), "dashboard-reports");

  const profile = createAsync(() => profileQuery());
  const datasets = createAsync(() => datasetsQuery());
  const reports = createAsync(() => reportsQuery());

  const recentActivity = () => {
    const analyzedDatasets = new Set((reports() ?? []).map((report) => report.dataset));

    return (datasets() ?? [])
      .slice()
      .sort((left, right) => right.created_at.localeCompare(left.created_at))
      .slice(0, 4)
      .map((dataset) => ({
        name: dataset.name,
        date: new Date(dataset.created_at).toLocaleString(),
        status: analyzedDatasets.has(dataset.id) ? "Analyzed" : "Uploaded",
      }));
  };

  const stats = () => [
    { label: "Total Datasets", value: String(datasets()?.length ?? 0), icon: Database, change: "Synced from server" },
    { label: "Reports Generated", value: String(reports()?.length ?? 0), icon: FileText, change: "Backend pipeline output" },
    { label: "Current User", value: profile()?.first_name || profile()?.email || "Signed in", icon: Activity, change: profile()?.username || "Authenticated session" },
    { label: "Latest Upload", value: datasets()?.[0]?.created_at ? new Date(datasets()![0].created_at).toLocaleDateString() : "None", icon: TrendingUp, change: "Most recent dataset" },
  ];

  const ready = () => Boolean(profile() && datasets() && reports());

  return (
    <div class="min-h-screen">
      <Navigation />
      <div class="max-w-7xl mx-auto px-6 py-8">
        <Show
          when={ready()}
          fallback={
            <div class="p-6 rounded-lg border border-border bg-card">
              Loading dashboard...
            </div>
          }
        >
          <div class="mb-8">
            <h1 class="mb-2">Dashboard</h1>
            <p class="text-muted-foreground">
              Overview of your data analytics and insights for {profile()?.first_name || profile()?.email}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <For each={stats()}>
              {(stat) => (
                <div class="p-6 rounded-lg border border-border bg-card">
                  <div class="flex items-center justify-between mb-4">
                    <stat.icon class="w-5 h-5 text-muted-foreground" />
                    <span class="text-xs text-muted-foreground">{stat.change}</span>
                  </div>
                  <div class="text-3xl mb-1">{stat.value}</div>
                  <div class="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              )}
            </For>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="p-6 rounded-lg border border-border bg-card">
              <h3 class="mb-6">Recent Activity</h3>
              <div class="space-y-4">
                <For each={recentActivity()}>
                  {(item) => (
                  <div class="flex items-center justify-between py-3 border-b border-border last:border-0">
                    <div>
                      <div class="mb-1">{item.name}</div>
                      <div class="text-sm text-muted-foreground">{item.date}</div>
                    </div>
                    <div class="px-3 py-1 rounded-full bg-accent text-accent-foreground text-sm">
                      {item.status}
                    </div>
                  </div>
                )}
                </For>
              </div>
            </div>

            <div class="p-6 rounded-lg border border-border bg-card">
              <h3 class="mb-6">Quick Actions</h3>
              <div class="space-y-3">
                <A
                  href="/upload"
                  class="block p-4 rounded-lg border border-border hover:border-foreground transition-colors"
                >
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Database class="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <div class="mb-1">Upload New Dataset</div>
                      <div class="text-sm text-muted-foreground">
                        Add CSV, XLS, or XLSX files
                      </div>
                    </div>
                  </div>
                </A>

                <A
                  href="/history"
                  class="block p-4 rounded-lg border border-border hover:border-foreground transition-colors"
                >
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <FileText class="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <div class="mb-1">View All Datasets</div>
                      <div class="text-sm text-muted-foreground">
                        Access past analyses and reports
                      </div>
                    </div>
                  </div>
                </A>
              </div>
            </div>
          </div>
        </Show>
      </div>
    </div>
  );
}
