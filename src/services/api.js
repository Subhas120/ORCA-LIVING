/*
 * ORCA M4 API SERVICE
 *
 * The frontend communicates only with the authoritative
 * M4 integration API.
 */

const DECISION_ENDPOINT =
  import.meta.env.VITE_ORCA_DECISION_ENDPOINT ||
  "http://localhost:8000/api/v1/decision";

export async function requestDecision(request) {
  const response = await fetch(
    DECISION_ENDPOINT,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    throw new Error(
      `ORCA M4 request failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}