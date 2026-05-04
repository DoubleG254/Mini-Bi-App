import { Navigation } from "../Navigation";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Filter, TrendingUp, TrendingDown, Minus } from "lucide-solid";
import { useParams } from "@solidjs/router";

export default function AnalyticsPage() {
  const { datasetId } = useParams();

  // Mock data - in production this would come from the backend based on datasetId
  const lineChartData = [
    { month: "Jan", math: 78, science: 82, english: 85, history: 80 },
    { month: "Feb", math: 82, science: 85, english: 88, history: 83 },
    { month: "Mar", math: 85, science: 88, english: 90, history: 86 },
    { month: "Apr", math: 88, science: 90, english: 92, history: 89 },
  ];

  const barChartData = [
    { subject: "Math", average: 83, students: 45 },
    { subject: "Science", average: 86, students: 42 },
    { subject: "English", average: 89, students: 48 },
    { subject: "History", average: 85, students: 44 },
  ];

  const pieChartData = [
    { name: "Excellent", value: 35, color: "oklch(0.646 0.222 41.116)" },
    { name: "Good", value: 40, color: "oklch(0.6 0.118 184.704)" },
    { name: "Average", value: 20, color: "oklch(0.828 0.189 84.429)" },
    { name: "Needs Improvement", value: 5, color: "oklch(0.769 0.188 70.08)" },
  ];

  const distributionData = [
    { range: "0-20", count: 2 },
    { range: "21-40", count: 5 },
    { range: "41-60", count: 12 },
    { range: "61-80", count: 28 },
    { range: "81-100", count: 33 },
  ];

  const metrics = [
    { label: "Average Score", value: "85.7", change: "+3.2", trend: "up" },
    { label: "Total Students", value: "179", change: "+12", trend: "up" },
    { label: "Pass Rate", value: "94.2%", change: "+1.8%", trend: "up" },
    { label: "Completion Rate", value: "96.1%", change: "0%", trend: "neutral" },
  ];
  
  return (
    <div class="min-h-screen">
      <Navigation />
      <div class="max-w-7xl mx-auto px-6 py-8">
        <div class="mb-8 flex items-center justify-between">
          <div>
            <h1 class="mb-2">Student Performance Analysis</h1>
            <p class="text-muted-foreground">Q1 2026 Academic Results</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric) => (
            <div class="p-6 rounded-lg border border-border bg-card">
              <div class="flex items-center justify-between mb-4">
                <span class="text-sm text-muted-foreground">{metric.label}</span>
                {metric.trend === "up" && (
                  <TrendingUp class="w-4 h-4 text-green-500" />
                )}
                {metric.trend === "down" && (
                  <TrendingDown class="w-4 h-4 text-red-500" />
                )}
                {metric.trend === "neutral" && (
                  <Minus class="w-4 h-4 text-muted-foreground" />
                )}
              </div>
              <div class="text-3xl mb-1">{metric.value}</div>
              <div class="text-sm text-muted-foreground">{metric.change}</div>
            </div>
          ))}
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div class="p-6 rounded-lg border border-border bg-card">
            <h3 class="mb-6">Performance Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" stroke="var(--muted-foreground)" />
                <YAxis stroke="var(--muted-foreground)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="math"
                  stroke="var(--chart-1)"
                  strokeWidth={2}
                  name="Math"
                />
                <Line
                  type="monotone"
                  dataKey="science"
                  stroke="var(--chart-2)"
                  strokeWidth={2}
                  name="Science"
                />
                <Line
                  type="monotone"
                  dataKey="english"
                  stroke="var(--chart-3)"
                  strokeWidth={2}
                  name="English"
                />
                <Line
                  type="monotone"
                  dataKey="history"
                  stroke="var(--chart-4)"
                  strokeWidth={2}
                  name="History"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div class="p-6 rounded-lg border border-border bg-card">
            <h3 class="mb-6">Subject Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="subject" stroke="var(--muted-foreground)" />
                <YAxis stroke="var(--muted-foreground)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="average" fill="var(--chart-1)" name="Average Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="p-6 rounded-lg border border-border bg-card">
            <h3 class="mb-6">Grade Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={100}
                  fill="var(--chart-1)"
                  dataKey="value"
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.5rem",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div class="p-6 rounded-lg border border-border bg-card">
            <h3 class="mb-6">Score Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="range" stroke="var(--muted-foreground)" />
                <YAxis stroke="var(--muted-foreground)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.5rem",
                  }}
                />
                <Bar dataKey="count" fill="var(--chart-2)" name="Students" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
