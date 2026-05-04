import { clearAuthSession, getAccessToken, getRefreshToken, setAuthSession } from "./auth";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

/** The type of result returned from the api */
export type ApiResult<T> = {
  /** A boolean to indicate whether or not a successful result was obtained */
  success: boolean;
  /** The result message associated with the response */
  message: string;
  /** The data returned from the  */
  data?: T;
  /** The error associated with the api result failure */
  error?: string;
  /** The url to redirect to */
  redirectTo?: string;
};

export type UserProfile = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
};

export type DatasetRecord = {
  id: number;
  user: number;
  name: string;
  file: string;
  created_at: string;
};

export type ReportRecord = {
  id: number;
  user: number;
  dataset: number;
  summary: Record<string, unknown>;
  charts: Record<string, ChartConfig>;
  created_at: string;
};

export type ChartConfig = {
  id: string;
  type: "line" | "bar" | "scatter" | string;
  title: string;
  labels?: string[];
  datasets: Array<{
    label: string;
    data: Array<number | { x: number; y: number }>;
    borderColor?: string;
    backgroundColor?: string;
    fill?: boolean;
    tension?: number;
  }>;
  correlation_coefficient?: number;
};

type RequestOptions = RequestInit & {
  auth?: boolean;
  retryOnAuthFailure?: boolean;
};

function buildUrl(path: string) {
  return path.startsWith("http") ? path : `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

async function parseJsonResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  return text ? (JSON.parse(text) as T) : ({} as T);
}

async function extractErrorMessage(response: Response) {
  try {
    const payload = await response.clone().json();
    if (typeof payload === "string") {
      return payload;
    }

    if (payload?.detail) {
      return String(payload.detail);
    }

    if (payload?.message) {
      return String(payload.message);
    }

    if (payload?.error) {
      return String(payload.error);
    }

    return JSON.stringify(payload);
  } catch {
    return response.statusText || "Request failed";
  }
}

async function refreshAuthSession() {
  const refresh = getRefreshToken();

  if (!refresh) {
    return false;
  }

  const response = await fetch(buildUrl("/token/refresh/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    clearAuthSession();
    return false;
  }

  const payload = await parseJsonResponse<{ access: string }>(response);
  if (payload.access) {
    setAuthSession({ access: payload.access, refresh });
    return true;
  }

  clearAuthSession();
  return false;
}

async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = true, retryOnAuthFailure = true, headers, body, ...rest } = options;
  const requestHeaders = new Headers(headers);

  if (!(body instanceof FormData) && body !== undefined && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }

  if (auth) {
    const token = getAccessToken();
    if (token) {
      requestHeaders.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(buildUrl(path), {
    ...rest,
    headers: requestHeaders,
    body,
  });

  if (response.status === 401 && auth && retryOnAuthFailure && (await refreshAuthSession())) {
    return requestJson<T>(path, {
      ...options,
      retryOnAuthFailure: false,
    });
  }

  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }

  return parseJsonResponse<T>(response);
}

export async function fetchCurrentUser() {
  return requestJson<UserProfile>("/profile/");
}

export async function loginWithEmail(email: string, password: string) {
  const session = await requestJson<{ access: string; refresh: string }>("/login/", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ username: email, password }),
  });

  setAuthSession({ access: session.access, refresh: session.refresh });
  return session;
}

export async function registerAccount(payload: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  password2: string;
}) {
  return requestJson<{ message: string }>("/register/", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
}

/**
 * A function that get's the user's stored session, and invalidates the refresh token associated with it
 * @returns The success or error message
 */
export async function logoutSession() {
  const refresh = getRefreshToken();

  if (!refresh) {
    clearAuthSession();
    return { message: "Signed out locally" };
  }

  const result = await requestJson<{ message: string }>("/logout/", {
    method: "POST",
    body: JSON.stringify({ refresh }),
  });

  clearAuthSession();
  return result;
}

export async function fetchDatasets() {
  return requestJson<DatasetRecord[]>("/datasets/");
}

export async function fetchReports() {
  return requestJson<ReportRecord[]>("/reports/");
}

export async function uploadDataset(file: File, name: string) {
  const formData = new FormData();
  formData.append("name", name);
  formData.append("file", file);

  return requestJson<DatasetRecord>("/datasets/", {
    method: "POST",
    body: formData,
  });
}

export function getDatasetBaseName(fileName: string) {
  return fileName.replace(/\.[^.]+$/, "").slice(0, 50);
}