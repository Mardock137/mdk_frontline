export const SESSION_COOKIE_NAME = "frontline_session";
export const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24;

export function readSessionToken(): string | null {
  if (typeof document === "undefined") {
    return null;
  }
  const prefix = `${SESSION_COOKIE_NAME}=`;
  const match = document.cookie
    .split("; ")
    .find((part) => part.startsWith(prefix));
  if (!match) {
    return null;
  }
  return decodeURIComponent(match.slice(prefix.length));
}
