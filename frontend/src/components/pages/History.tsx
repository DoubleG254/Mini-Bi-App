import { A, createAsync, query } from "@solidjs/router";
import { Navigation } from "../Navigation";
import { FileSpreadsheet, Calendar, Eye } from "lucide-solid";
import { For, Show } from "solid-js";

type DatasetType = {
  id: string,
  name: string,
  uploadDate: Date,
  records: number,
  columns: number,
}

export default function HistoryPage() {
  // Call server api
  const fetchDatasets = query<() => Promise<DatasetType[]>>(async () => {
    // Call the endpoint
    return []
  }, "history-datasets")

  const datasets = createAsync(() => fetchDatasets())

  return (
    <div class="min-h-screen">
      <Navigation />
      <div class="max-w-7xl mx-auto px-6 py-8">
        <div class="mb-8 flex items-center justify-between">
          <div>
            <h1 class="mb-2">Dataset History</h1>
            <p class="text-muted-foreground">
              View and manage your uploaded datasets
            </p>
          </div>
        </div>

        <Show when={datasets()?.length} fallback={
          <div class="text-center py-12">
            <p class="text-muted-foreground">
              No datasets founds
            </p>
          </div>
        }>
          <div class="space-y-4">
            <For each={datasets()}>{(dataset) => (
              <div
                class="p-6 rounded-lg border border-border bg-card hover:border-foreground transition-colors"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-4 flex-1">
                    <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                      <FileSpreadsheet class="w-6 h-6 text-primary" />
                    </div>

                    <h3 class="mb-2">{dataset.name}</h3>
                  </div>

                  <A
                    href={`/analytics/${dataset.id}`}
                    class="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity"
                  >
                    <Eye class="w-4 h-4" />
                    View Analysis
                  </A>
                </div>
              </div>
            )}</For>
          </div>
        </Show>
      </div>
    </div>
  );
}
