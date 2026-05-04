import { For } from "solid-js";
import { Navigation } from "../Navigation";
import { TrendingUp, Database, FileText, Activity } from "lucide-solid";
import { A } from "@solidjs/router";

export default function DashboardPage() {
  const stats = [
    { label: "Total Datasets", value: "24", icon: Database, change: "+3 this week" },
    { label: "Active Analyses", value: "8", icon: Activity, change: "2 in progress" },
    { label: "Reports Generated", value: "156", icon: FileText, change: "+12 this month" },
    { label: "Data Points", value: "2.4M", icon: TrendingUp, change: "+180K" },
  ];

  const recentActivity = [
    { name: "Student Performance Q1", date: "2 hours ago", status: "Completed" },
    { name: "Sales Analysis 2026", date: "5 hours ago", status: "Completed" },
    { name: "Survey Results March", date: "1 day ago", status: "Completed" },
    { name: "Inventory Data", date: "2 days ago", status: "Completed" },
  ];

  return (
    <div class="min-h-screen">
      <Navigation />
      <div class="max-w-7xl mx-auto px-6 py-8">
        <div class="mb-8">
          <h1 class="mb-2">Dashboard</h1>
          <p class="text-muted-foreground">
            Overview of your data analytics and insights
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <For each={stats}>
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
              <For each={recentActivity}>
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
      </div>
    </div>
  );
}
