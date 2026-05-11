import { Navigation } from "../Navigation";
import { TrendingUp, TrendingDown, Minus } from "lucide-solid";
import { createAsync, query, useParams } from "@solidjs/router";
import { For, Show, Switch, Match, onMount } from "solid-js";
import { fetchDatasets, fetchReports, type ChartConfig } from "../../lib/api";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ScatterController,
  LineController,
  BarController,
  Chart,
  ChartData,
  ChartOptions,
  ChartType,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ScatterController,
  LineController,
  BarController
);

type ChartPoint = Record<string, string | number>;

// Helper component to render a Chart.js chart
const ChartComponent = (props: { chartConfig: any; title: string }) => {
  let canvasRef: HTMLCanvasElement | undefined;

  onMount(() => {
    if (!canvasRef) return;
    
    // Destroy previous instance if exists
    const existingChart = Chart.getChart(canvasRef);
    if (existingChart) {
      existingChart.destroy();
    }

    const newChart = new Chart(canvasRef, {
      type: props.chartConfig.type,
      data: props.chartConfig.data,
      options: props.chartConfig.options,
    });

    // Cleanup on unmount
    return () => {
      if (newChart) newChart.destroy();
    };
  });

  return (
    <div class="h-[350px] w-full">
      <canvas ref={canvasRef} />
    </div>
  );
};

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
    if (!value) return "Unavailable";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
  };

  const trendIcon = (trend: string) => {
    switch (trend) {
      case "up": return <TrendingUp class="w-4 h-4 text-green-500" />;
      case "down": return <TrendingDown class="w-4 h-4 text-red-500" />;
      default: return <Minus class="w-4 h-4 text-muted-foreground" />;
    }
  };

  const metrics = () => {
    const summary = summaryEntries();
    const semanticCounts = summary.reduce<Record<string, number>>((acc, [, value]) => {
      const semantic = (value as { semantic?: string } | undefined)?.semantic ?? "other";
      acc[semantic] = (acc[semantic] ?? 0) + 1;
      return acc;
    }, {});

    return [
      { label: "Columns Analyzed", value: String(summary.length), change: "From report summary", trend: "up" },
      { label: "Financial Columns", value: String(semanticCounts.financial_total ?? 0), change: "Detected by backend", trend: "up" },
      { label: "Time Fields", value: String((semanticCounts.date ?? 0) + (semanticCounts.timestamp ?? 0) + (semanticCounts.time_period ?? 0)), change: "Temporal dimensions", trend: "neutral" },
      { label: "Dataset Name", value: dataset()?.name ?? "Unknown", change: formatDate(dataset()?.created_at), trend: "neutral" },
    ];
  };

  const getChartConfig = (chart: ChartConfig) => {
    const labels = chart.labels ?? [];
    const datasets = chart.datasets ?? [];

    if (chart.type === "scatter") {
      const scatterPoints = datasets.flatMap((series) => {
        if (!Array.isArray(series.data)) return [];
        return series.data
          .filter((p: any) => p && typeof p.x === 'number' && typeof p.y === 'number')
          .map((p: any) => ({ x: p.x, y: p.y }));
      });

      return {
        type: "scatter" as ChartType,
        data: {
          datasets: [{
            label: chart.datasets?.label || "Data Points",
            data: scatterPoints,
            backgroundColor: chart.datasets?.backgroundColor || "rgba(54, 162, 235, 0.6)",
            borderColor: chart.datasets?.borderColor || "rgba(54, 162, 235, 1)",
            borderWidth: 1,
            pointRadius: 4,
            pointHoverRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { type: "linear" as const, position: "bottom" as const, title: { display: true, text: "X Axis" } },
            y: { type: "linear" as const, title: { display: true, text: "Y Axis" } },
          },
          plugins: {
            legend: { display: true },
            tooltip: {
              callbacks: {
                label: (context: any) => `(${context.parsed.x}, ${context.parsed.y})`,
              },
            },
          },
        } as ChartOptions<"scatter">,
      };
    }

    const chartDatasets = datasets.map((series, index) => ({
      label: series.label,
      data: series.data,
      borderColor: series.borderColor || `hsl(${index * 60}, 70%, 50%)`,
      backgroundColor: series.backgroundColor || `hsl(${index * 60}, 70%, 50%, 0.2)`,
      tension: 0.4,
      borderWidth: 2,
    }));

    return {
      type: chart.type as ChartType,
      data: { labels, datasets: chartDatasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { x: { display: true }, y: { display: true } },
        plugins: { legend: { display: true } },
      } as ChartOptions,
    };
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
              <h1 class="mb-2 text-2xl font-bold">{dataset()?.name ?? "Dataset Analysis"}</h1>
              <p class="text-muted-foreground">{formatDate(dataset()?.created_at)}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <For each={metrics()}>
              {(metric) => (
                <div class="p-6 rounded-lg border border-border bg-card shadow-sm">
                  <div class="flex items-center justify-between mb-4">
                    <span class="text-sm text-muted-foreground">{metric.label}</span>
                    {trendIcon(metric.trend)}
                  </div>
                  <div class="text-3xl font-bold mb-1">{metric.value}</div>
                  <div class="text-sm text-muted-foreground">{metric.change}</div>
                </div>
              )}
            </For>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <For each={charts()}>
              {(chart) => {
                const config = getChartConfig(chart);
                return (
                  <div class="p-6 rounded-lg border border-border bg-card shadow-sm">
                    <h3 class="mb-4 text-lg font-semibold">{chart.title}</h3>
                    <ChartComponent chartConfig={config} title={chart.title} />
                  </div>
                );
              }}
            </For>
          </div>

          <div class="p-6 rounded-lg border border-border bg-card shadow-sm">
            <h3 class="mb-6 text-lg font-semibold">Column Summary</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <For each={summaryEntries()}>
                {([columnName, details]) => (
                  <div class="rounded-lg border border-border p-4 bg-card/50">
                    <div class="mb-2 font-medium text-base">{columnName}</div>
                    <pre class="text-xs whitespace-pre-wrap text-muted-foreground font-mono">
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