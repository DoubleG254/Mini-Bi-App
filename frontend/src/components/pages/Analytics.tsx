import { Navigation } from "../Navigation";
import { TrendingUp, TrendingDown, Minus } from "lucide-solid";
import { createAsync, query, useParams } from "@solidjs/router";
import { For, Show, Switch, Match, onCleanup, onMount, createSignal, createEffect } from "solid-js";
import { fetchDatasets, fetchReports, type ChartConfig } from "../../lib/api";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  ScatterController,
  LineController,
  BarController,
  PieController,
  Chart,
  ChartOptions,
  ChartType,
} from "chart.js";
import {SolidMarkdown} from "solid-markdown"

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  ScatterController,
  LineController,
  BarController,
  PieController
);

const md = new MarkdownIt();

type ChartPoint = Record<string, string | number>;

// Helper component to render a Chart.js chart
const ChartComponent = (props: { chartConfig: any; title: string }) => {
  let canvasRef: HTMLCanvasElement | undefined;
  let chartInstance: Chart | undefined;
  let frameId: number | null = null;

  onMount(() => {
    frameId = window.requestAnimationFrame(() => {
      if (!canvasRef) return;

      const existingChart = Chart.getChart(canvasRef);
      if (existingChart) {
        existingChart.destroy();
      }

      chartInstance = new Chart(canvasRef, {
        type: props.chartConfig.type,
        data: props.chartConfig.data,
        options: props.chartConfig.options,
      });
    });
  });

  onCleanup(() => {
    if (frameId !== null) {
      window.cancelAnimationFrame(frameId);
    }

    chartInstance?.destroy();
  });

  return (
    <div class="h-87.5 w-full">
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
  const charts = () => {
    const payload = report()?.charts ?? [];
    return Array.isArray(payload) ? payload : Object.values(payload);
  };

  // Lazy/sequential chart mounting to avoid blocking the main thread
  const [visibleCount, setVisibleCount] = createSignal(0);
  let rafId: number | null = null;

  createEffect(() => {
    const list = charts();
    setVisibleCount(0);
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    if (!list || list.length === 0) return;
    let i = 0;
    function step() {
      i += 1;
      setVisibleCount(i);
      if (i < list.length) {
        rafId = window.requestAnimationFrame(step);
      } else {
        rafId = null;
      }
    }
    rafId = window.requestAnimationFrame(step);
  });

  onCleanup(() => {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
  });


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
    ];
  };

  const getChartConfig = (chart: ChartConfig) => {
    const labels = chart.labels ?? [];
    const datasets = chart.datasets ?? [];

    if (chart.type === "pie") {
      const firstDataset = datasets[0];

      return {
        type: "pie" as ChartType,
        data: {
          labels,
          datasets: [{
            label: firstDataset?.label ?? "Distribution",
            data: firstDataset?.data ?? [],
            backgroundColor: Array.isArray(firstDataset?.backgroundColor)
              ? firstDataset?.backgroundColor
              : [
                  "rgba(255, 99, 132, 0.8)",
                  "rgba(54, 162, 235, 0.8)",
                  "rgba(255, 206, 86, 0.8)",
                  "rgba(75, 192, 192, 0.8)",
                  "rgba(153, 102, 255, 0.8)",
                  "rgba(255, 159, 64, 0.8)",
                ],
            borderColor: Array.isArray(firstDataset?.borderColor)
              ? firstDataset?.borderColor
              : [
                  "rgb(255, 99, 132)",
                  "rgb(54, 162, 235)",
                  "rgb(255, 206, 86)",
                  "rgb(75, 192, 192)",
                  "rgb(153, 102, 255)",
                  "rgb(255, 159, 64)",
                ],
            borderWidth: firstDataset?.borderWidth ?? 2,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: true },
          },
        } as ChartOptions<"pie">,
      };
    }

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
            label: datasets[0]?.label || "Data Points",
            data: scatterPoints,
            backgroundColor: datasets[0]?.backgroundColor || "rgba(54, 162, 235, 0.6)",
            borderColor: datasets[0]?.borderColor || "rgba(54, 162, 235, 1)",
            borderWidth: datasets[0]?.borderWidth ?? 1,
            pointRadius: datasets[0]?.pointRadius ?? 4,
            pointHoverRadius: datasets[0]?.pointHoverRadius ?? 6,
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
      borderWidth: series.borderWidth ?? 2,
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

          <div class="flex justify-start items-center w-full gap-2">
            <For each={metrics()}>
              {(metric) => (
                <div class="p-6 rounded-lg border border-border bg-card shadow-sm w-full">
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
            <For each={charts().slice(0, visibleCount())}>
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
                    <div class="text-xs whitespace-pre-wrap text-muted-foreground font-mono" >                      
                      <SolidMarkdown renderingStrategy="reconcile">{details}</SolidMarkdown>
                    </div>
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