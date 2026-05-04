import { A, useNavigate } from "@solidjs/router";
import { createSignal, Show, Switch, Match } from "solid-js";
import { ChartBarIcon } from "lucide-solid";
import { loginWithEmail, type ApiResult } from "../../lib/api";

export default function SignInPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = createSignal(false);
  const [result, setResult] = createSignal<ApiResult<null> | null>(null);

  const handleSubmit = async (event: SubmitEvent) => {
    event.preventDefault();

    const formData = new FormData(event.currentTarget as HTMLFormElement);
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");

    setLoading(true);
    setResult(null);

    try {
      await loginWithEmail(email, password);

      const nextResult: ApiResult<null> = {
        success: true,
        message: "Signed in successfully",
        redirectTo: "/dashboard",
      };

      setResult(nextResult);
      navigate(nextResult.redirectTo ?? "/dashboard", { replace: true });
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : "Unable to sign in",
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
            <Show when={loading()} fallback="Sign In">
              Signing In...
            </Show>
          </button>
        </form>

        <p class="mt-6 text-center text-muted-foreground">
          Don't have an account?{" "}
          <A href="/register" class="text-foreground hover:underline">
            Register
          </A>
        </p>
      </div>
    </div>
  );
}
