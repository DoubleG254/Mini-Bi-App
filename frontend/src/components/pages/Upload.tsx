import { useNavigate } from "@solidjs/router";
import { Navigation } from "../Navigation";
import { Upload as UploadIcon, FileSpreadsheet, CircleCheckIcon } from "lucide-solid";
import { createSignal, Show, Switch, Match } from "solid-js";
import { JSX } from "solid-js/h/jsx-runtime";
import { getDatasetBaseName, type ApiResult, uploadDataset } from "../../lib/api";

export default function UploadPage() {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = createSignal(false);
  const [file, setFile] = createSignal<File | null>(null);
  const [uploading, setUploading] = createSignal(false);
  const [result, setResult] = createSignal<ApiResult<{ id: number }> | null>(null);

  const handleDragOver: JSX.EventHandler<HTMLDivElement, DragEvent> = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop: JSX.EventHandler<HTMLDivElement, DragEvent> = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer?.files[0];
    if (droppedFile && isValidFile(droppedFile)) {
      setFile(droppedFile);
    }
  };

  const handleFileSelect: JSX.EventHandler<HTMLInputElement, InputEvent> = (e) => {
    const selectedFile = e.currentTarget.files?.[0];

    if (selectedFile && isValidFile(selectedFile)) {
      setFile(selectedFile);
    }
  };

  const isValidFile = (file: File) => {
    const validTypes = [
      "text/csv",
      "application/vnd.ms-excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ];

    return validTypes.includes(file.type) || file.name.match(/\.(csv|xls|xlsx)$/i);
  };

  const handleUpload = async () => {
    if (!file()) {
      return;
    }

    setUploading(true);
    setResult(null);

    try {
      const dataset = await uploadDataset(file()!, getDatasetBaseName(file()!.name));

      const nextResult: ApiResult<{ id: number }> = {
        success: true,
        message: "Dataset uploaded and analysis started successfully",
        data: { id: dataset.id },
        redirectTo: `/analytics/${dataset.id}`,
      };

      setResult(nextResult);
      navigate(nextResult.redirectTo ?? `/analytics/${dataset.id}`, { replace: true });
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : "Unable to upload dataset",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div class="min-h-screen">
      <Navigation />
      <div class="max-w-4xl mx-auto px-6 py-8">
        <div class="mb-8">
          <h1 class="mb-2">Upload Dataset</h1>
          <p class="text-muted-foreground">
            Upload your CSV, XLS, or XLSX file for analysis
          </p>
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          class={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging() ? "border-primary bg-primary/5" : "border-border bg-card"}`}
        >
          <input
            type="file"
            accept=".csv,.xls,.xlsx"
            onInput={handleFileSelect}
            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          <Show when={file()} fallback={
            <div class="space-y-4">
              <div class="flex justify-center">
                <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <UploadIcon class="w-8 h-8 text-primary" />
                </div>
              </div>
              <div>
                <h3 class="mb-2">Drop your file here</h3>
                <p class="text-muted-foreground">
                  or click to browse from your computer
                </p>
              </div>
              <p class="text-sm text-muted-foreground">
                Supported formats: CSV, XLS, XLSX (Max 50MB)
              </p>
            </div>
          }>
            <div class="space-y-4">
              <div class="flex justify-center">
                <div class="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center">
                  <CircleCheckIcon class="w-8 h-8 text-green-500" />
                </div>
              </div>
              <div>
                <div class="flex items-center justify-center gap-2 mb-2">
                  <FileSpreadsheet class="w-5 h-5 text-muted-foreground" />
                  <h3>{file()?.name}</h3>
                </div>
                <p class="text-muted-foreground">
                  {(file()!.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={() => setFile(null)}
                class="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Remove file
              </button>
            </div>

            <div class="mt-8 flex justify-end">
              <button
                onClick={handleUpload}
                disabled={uploading()}
                class="px-6 py-3 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                <Show when={uploading()} fallback="Upload & Analyze">Analyzing...</Show>
              </button>
            </div>

            <Show when={result()}>
              <div class={`mt-6 rounded-lg border px-4 py-3 text-sm ${result()?.success ? "border-green-500/30 bg-green-500/10 text-green-700" : "border-red-500/30 bg-red-500/10 text-red-600"}`}>
                <Switch>
                  <Match when={result()?.success}>{result()?.message}</Match>
                  <Match when={!result()?.success}>{result()?.message}</Match>
                </Switch>
              </div>
            </Show>
          </Show>
        </div>
      </div>
    </div>
  );
}
