import { A } from "@solidjs/router";
import { createSignal, Show, Switch, Match } from "solid-js";
import { ChartBarIcon } from "lucide-solid";
import { registerAccount, type ApiResult } from "../../lib/api";

export default function RegisterPage() {
  const [loading, setLoading] = createSignal(false);
  const [result, setResult] = createSignal<ApiResult<null> | null>(null);

  const handleSubmit = async (event: SubmitEvent) => {
    event.preventDefault();

    const formData = new FormData(event.currentTarget as HTMLFormElement);
    const first_name = String(formData.get("first_name") ?? "").trim();
    const last_name = String(formData.get("last_name") ?? "").trim();
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");
    const password2 = String(formData.get("password2") ?? "");

    setLoading(true);
    setResult(null);

    try {
      const response = await registerAccount({
        first_name,
        last_name,
        email,
        password,
        password2,
      });

      setResult({
        success: true,
        message: response.message ?? "Account created successfully. Sign in to continue.",
      });
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : "Unable to create account",
      });
    } finally {
      setLoading(false);
    }
  };

  const statusClass = () => {
    if (result()?.success) {
      return "border-green-500/30 bg-green-500/10 text-green-700";
    }

    return "border-red-500/30 bg-red-500/10 text-red-600";
  };

  return (
    <div class="min-h-screen flex items-center justify-center px-4">
      <div class="w-full max-w-md">
        <div class="flex items-center justify-center gap-3 mb-12">
          <div class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <ChartBarIcon class="w-6 h-6 text-primary-foreground" />
          </div>
          <h1 class="text-3xl tracking-tight">DataInsight</h1>
        </div>

        <form onSubmit={handleSubmit} class="space-y-6">
          <div>
            <label for="first_name" class="block mb-2">
              First Name
            </label>
            <input
              id="first_name"
              name="first_name"
              type="text"
              required
              class="w-full px-4 py-3 rounded-lg bg-input-background border border-border focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="John"
            />
          </div>

          <div>
            <label for="last_name" class="block mb-2">
              Last Name
            </label>
            <input
              id="last_name"
              name="last_name"
              type="text"
              required
              class="w-full px-4 py-3 rounded-lg bg-input-background border border-border focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Doe"
            />
          </div>

          <div>
            <label for="email" class="block mb-2">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              class="w-full px-4 py-3 rounded-lg bg-input-background border border-border focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label for="password" class="block mb-2">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              class="w-full px-4 py-3 rounded-lg bg-input-background border border-border focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label for="password2" class="block mb-2">
              Confirm Password
            </label>
            <input
              id="password2"
              name="password2"
              type="password"
              required
              class="w-full px-4 py-3 rounded-lg bg-input-background border border-border focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="••••••••"
            />
          </div>

          <Show when={result()}>
            <div class={`rounded-lg border px-4 py-3 text-sm ${statusClass()}`}>
              <Switch>
                <Match when={result()?.success}>{result()?.message}</Match>
                <Match when={!result()?.success}>{result()?.message}</Match>
              </Switch>
            </div>
          </Show>

          <button
            type="submit"
            disabled={loading()}
            class="w-full px-4 py-3 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-60"
          >
            <Show when={loading()} fallback="Create Account">
              Creating Account...
            </Show>
          </button>
        </form>

        <p class="mt-6 text-center text-muted-foreground">
          Already have an account?{" "}
          <A href="/" class="text-foreground hover:underline">
            Sign In
          </A>
        </p>
      </div>
    </div>
  );
}
