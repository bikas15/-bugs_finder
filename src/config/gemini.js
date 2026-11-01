import { API_BASE_URL } from "./apiBaseUrl";

async function run(prompt) {
  const accessToken = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE_URL}analysis/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({ prompt }),
  });
  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.detail || "Code analysis request failed.");
  }
  if (typeof result.response !== "string" || !result.response.trim()) {
    throw new Error("The code analysis service returned an empty response.");
  }

  return result.response;
}

export default run;
