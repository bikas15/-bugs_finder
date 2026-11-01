import { API_BASE_URL } from "../../config/apiBaseUrl";

export const executeCode = async (language, sourceCode, input = "") => {
  const accessToken = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE_URL}execute/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({
      language,
      code: sourceCode,
      input,
    }),
  });

  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error("The code execution service returned an invalid response.");
  }
  if (!response.ok) {
    throw new Error(result.detail || "Code execution request failed.");
  }
  if (typeof result.output !== "string" || !Number.isInteger(result.exit_code)) {
    throw new Error("The code execution service returned an invalid response.");
  }

  return {
    output: result.output,
    exitCode: result.exit_code,
  };
};
