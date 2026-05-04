import { Navigation } from "../Navigation";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, TrendingDown, Minus } from "lucide-solid";
import { createAsync, query, useParams } from "@solidjs/router";
import { For, Show, Switch, Match } from "solid-js";
import { fetchDatasets, fetchReports, type ChartConfig } from "../../lib/api";

type ChartPoint = Record<string, string | number>;

export default function AnalyticsPage() {
  const params = useParams();
  const datasetId = () => Number(params.datasetId);

  const reportsQuery = query(async () => fetchReports(), "analytics-reports");
  const datasetsQuery = query(async () => fetchDatasets(), "analytics-datasets");

  const reports = createAsync(() => reportsQuery());
  const datasets = createAsync(() => datasetsQuery());

  const report = () => (reports() ?? []).find((item) => item.dataset === datasetId());
  const dataset = () => (datasets() ?? []).find((item) => item.id === datasetId());

  const summaryEntries = () => Object.entries(report()?.summary ?? {});
  const charts = () => Object.values(report()?.charts ?? {});

  const formatDate = (value?: string) => {
    if (!value) {
      return "Unavailable";
    }

    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
  };

  const buildChartRows = (chart: ChartConfig): ChartPoint[] => {
    const rows: ChartPoint[] = [];
    const labels = chart.labels ?? [];
    const datasets = chart.datasets ?? [];

    labels.forEach((label, index) => {
      const row: ChartPoint = { label };

      datasets.forEach((series) => {
        const value = series.data[index];
        if (typeof value === "number") {
          row[series.label] = value;
        }
      });

      rows.push(row);
    });

    return rows;
  };

  const trendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp class="w-4 h-4 text-green-500" />;
      case "down":
        return <TrendingDown class="w-4 h-4 text-red-500" />;
      default:
        return <Minus class="w-4 h-4 text-muted-foreground" />;
    }
  };

  const metrics = () => {
    const summary = summaryEntries();
    const semanticCounts = summary.reduce<Record<string, number>>((accumulator, [, value]) => {
      const semantic = (value as { semantic?: string } | undefined)?.semantic ?? "other";
      accumulator[semantic] = (accumulator[semantic] ?? 0) + 1;
      return accumulator;
    }, {});

    return [
      { label: "Columns Analyzed", value: String(summary.length), change: "From report summary", trend: "up" },
      { label: "Financial Columns", value: String(semanticCounts.financial_total ?? 0), change: "Detected by backend", trend: "up" },
      { label: "Time Fields", value: String((semanticCounts.date ?? 0) + (semanticCounts.timestamp ?? 0) + (semanticCounts.time_period ?? 0)), change: "Temporal dimensions", trend: "neutral" },
      { label: "Dataset Name", value: dataset()?.name ?? "Unknown", change: formatDate(dataset()?.created_at), trend: "neutral" },
    ];
  };

  return (
    <div class="min-h-screen">
      <Navigation />
      <div class="max-w-7xl mx-auto px-6 py-8">
        <Show
          when={report()}
          fallback={
            <div class="p-6 rounded-lg border border-border bg-card">
              <Switch>
                <Match when={!datasetId()}>No dataset id supplied.</Match>
                <Match when={true}>No analysis found for this dataset yet.</Match>
              </Switch>
            </div>
          }
        >
          <div class="mb-8 flex items-center justify-between">
            <div>
              <h1 class="mb-2">{dataset()?.name ?? "Dataset Analysis"}</h1>
              <p class="text-muted-foreground">{formatDate(dataset()?.created_at)}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <For each={metrics()}>
              {(metric) => (
                <div class="p-6 rounded-lg border border-border bg-card">
                  <div class="flex items-center justify-between mb-4">
                    <span class="text-sm text-muted-foreground">{metric.label}</span>
                    {trendIcon(metric.trend)}
                  </div>
                  <div class="text-3xl mb-1">{metric.value}</div>
                  <div class="text-sm text-muted-foreground">{metric.change}</div>
                </div>
              )}
            </For>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <For each={charts()}>
              {(chart) => (
                <div class="p-6 rounded-lg border border-border bg-card">
                  <h3 class="mb-6">{chart.title}</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <Switch>
                      <Match when={chart.type === "line"}>
                        <LineChart data={buildChartRows(chart)}>
                          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                          <XAxis dataKey="label" stroke="var(--muted-foreground)" />
                          <YAxis stroke="var(--muted-foreground)" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "var(--card)",
                              border: "1px solid var(--border)",
                              borderRadius: "0.5rem",
                            }}
                          />
                          <Legend />
                          <For each={chart.datasets}>
                            {(series, index) => (
                              <Line
                                type="monotone"
                                dataKey={series.label}
                                stroke={series.borderColor ?? `var(--chart-${(index() % 5) + 1})`}
                                strokeWidth={2}
                                name={series.label}
                              />
                            )}
                          </For>
                        </LineChart>
                      </Match>
                      <Match when={chart.type === "bar"}>
                        <BarChart data={buildChartRows(chart)}>
                          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                          <XAxis dataKey="label" stroke="var(--muted-foreground)" />
                          <YAxis stroke="var(--muted-foreground)" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "var(--card)",
                              border: "1px solid var(--border)",
                              borderRadius: "0.5rem",
                            }}
                          />
                          <Legend />
                          <For each={chart.datasets}>
                            {(series) => (
                              <Bar
                                dataKey={series.label}
                                fill={series.backgroundColor ?? "var(--chart-1)"}
                                name={series.label}
                              />
                            )}
                          </For>
                        </BarChart>
                      </Match>
                      <Match when={chart.type === "scatter"}>
                        <ScatterChart>
                          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                          <XAxis type="number" dataKey="x" stroke="var(--muted-foreground)" />
                          <YAxis type="number" dataKey="y" stroke="var(--muted-foreground)" />
                          <Tooltip
                            cursor={{ strokeDasharray: "3 3" }}
                            contentStyle={{
                              backgroundColor: "var(--card)",
                              border: "1px solid var(--border)",
                              borderRadius: "0.5rem",
                            }}
                          />
                          <Legend />
                          <For each={chart.datasets}>
                            {(series) => (
                              <Scatter
                                name={series.label}
                                data={series.data.filter(
                                  (point): point is { x: number; y: number } => typeof point === "object",
                                )}
                                fill={series.backgroundColor ?? "var(--chart-2)"}
                              />
                            )}
                          </For>
                        </ScatterChart>
                      </Match>
                      <Match when={true}>
                        <div class="flex h-full items-center justify-center text-sm text-muted-foreground">
                          Unsupported chart type: {chart.type}
                        </div>
                      </Match>
                    </Switch>
                  </ResponsiveContainer>
                </div>
              )}
            </For>
          </div>

          <div class="p-6 rounded-lg border border-border bg-card">
            <h3 class="mb-6">Column Summary</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <For each={summaryEntries()}>
                {([columnName, details]) => (
                  <div class="rounded-lg border border-border p-4">
                    <div class="mb-2 font-medium">{columnName}</div>
                    <pre class="text-xs whitespace-pre-wrap text-muted-foreground">
                      {JSON.stringify(details, null, 2)}
                    </pre>
                  </div>
                )}
              </For>
            </div>
          </div>
        </Show>
      </div>
    </div>
  );
}