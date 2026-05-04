import { useNavigate } from "@solidjs/router";
import { Navigation } from "../Navigation";
import { Upload as UploadIcon, FileSpreadsheet, CircleCheckIcon } from "lucide-solid";
import { createSignal, Show } from "solid-js";
import { JSX } from "solid-js/h/jsx-runtime";

export default function UploadPage() {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = createSignal(false);
  const [file, setFile] = createSignal<File | null>(null);
  const [uploading, setUploading] = createSignal(false);

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

  // Handler to api
  const handleUpload = async () => {
    if (!file()) return;

    setUploading(true);
    // Mock upload and analysis - in production this would call the backend
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Navigate to analytics with mock dataset ID
    navigate("/analytics/new-dataset");
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
          on:dragover={handleDragOver}
          on:dragleave={handleDragLeave}
          on:drop={handleDrop}
          class={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging()
            ? "border-primary bg-primary/5"
            : "border-border bg-card"
            }`}
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
                  <h3>{file.name}</h3>
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
          </Show>
        </div>
      </div>
    </div>
  );
}
