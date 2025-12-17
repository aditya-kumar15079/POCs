const BASE_URL = import.meta.env.VITE_API_BASE;

const GET = async (endpoint, params = {}) => {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${BASE_URL}${endpoint}${query ? "?" + query : ""}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${sessionStorage.getItem("authToken") || ""}`,
    },
  });
  if (response.status === 403) throw new Error(response.status);
  if (!response.ok) throw new Error(`GET ${endpoint} failed`);
  return response.json();
};

const POST = async (endpoint, body = {}, params = {}) => {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${BASE_URL}${endpoint}${query ? "?" + query : ""}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${sessionStorage.getItem("authToken") || ""}`,
    },
    body: JSON.stringify({ ...body }),
  });
  if (response.status === 403) throw new Error(response.status);
  if (!response.ok) throw new Error(`POST ${endpoint} failed`);
  return response.json();
};

const loginApi = async ({ username, password }) => {
  return POST("/auth/login", { username, password });
}

const chatHistoryApi = async ({ sessionId }) => {
  return GET(`/chat/history/${sessionId}`);
};

const chatStreamApi = async ({ payload, onChunk, onError, onComplete }) => {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${sessionStorage.getItem("authToken") || ""}`
      },
      body: JSON.stringify({ ...payload }),
    });

    if (!res.body) throw new Error("No response body");
    if (res.status === 403) throw new Error(`Not Authenticated`);
    if (!res.ok) throw new Error(`Streaming chat failed`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const part of parts) {
        if (part.startsWith("data:")) {
          try {
            const json = JSON.parse(part.replace("data: ", ""));
            if (json.type === "text") {
              onChunk(json.content);
            } else if (json.type === "end") {
              onComplete();
            }
          } catch (err) {
            console.error("Parse error", err);
          }
        }
      }
    }
  } catch (err) {
    onError(err.message);
  }
}

export { loginApi, chatHistoryApi, chatStreamApi };
