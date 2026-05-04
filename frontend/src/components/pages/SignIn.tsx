import { A, action, redirect } from "@solidjs/router";
import { ChartBarIcon } from "lucide-solid";

type ParsedFormData = {
  email: string
  password: string
}

export default function SignInPage() {
  // Handler to api
  const handleSubmit = action((formData: FormData) => {
    // Mock authentication - in production this would call the backend
    throw redirect("/dashboard");
  })

  return (
    <div class="min-h-screen flex items-center justify-center px-4">
      <div class="w-full max-w-md">
        <div class="flex items-center justify-center gap-3 mb-12">
          <div class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <ChartBarIcon class="w-6 h-6 text-primary-foreground" />
          </div>
          <h1 class="text-3xl tracking-tight">DataInsight</h1>
        </div>

        <form action={handleSubmit} method="post" class="space-y-6">
          <div>
            <label for="email" class="block mb-2">
              Email
            </label>
            <input
              id="email"
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
              type="password"
              required
              class="w-full px-4 py-3 rounded-lg bg-input-background border border-border focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            class="w-full px-4 py-3 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity"
          >
            Sign In
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
