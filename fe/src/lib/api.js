const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof body === "object" && body !== null
        ? body.detail || JSON.stringify(body)
        : body || response.statusText;
    throw new Error(`${response.status} ${detail}`);
  }

  return body;
}

export async function apiRequest(path, { method = "GET", role, body } = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "x-user-role": role,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  return parseResponse(response);
}

export { API_BASE_URL };
