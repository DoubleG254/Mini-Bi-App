/** The unique ID of the refresh token in localstorage */
const ACCESS_TOKEN_KEY = "mini-bi-access-token";
/** The unique ID of the refresh token in localstorage */
const REFRESH_TOKEN_KEY = "mini-bi-refresh-token";

/** The type of session data managed within the app */
export type AuthSession = {
  /** The access token */
  access: string;
  /** The refresh token */
  refresh: string;
};

/** A function to get the access token from localstorage */
export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/** A function to get the refresh token from localstorage */
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/** A function to set a new session for the user */
export function setAuthSession(session: AuthSession) {
  localStorage.setItem(ACCESS_TOKEN_KEY, session.access);
  localStorage.setItem(REFRESH_TOKEN_KEY, session.refresh);
}

/** A function to clear the existing user's session */
export function clearAuthSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/** A function to check if a user is authenticated */
export function isAuthenticated() {
  return Boolean(getAccessToken() && getRefreshToken());
}