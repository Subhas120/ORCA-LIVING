const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

/*
 * M3 API SERVICE
 *
 * This file is the only place where the frontend
 * communicates with the ORCA backend.
 *
 * The backend will provide REAL-TIME data.
 * We do not create or substitute mock data here.
 */

async function request(endpoint, options = {}) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}


/*
 * Get the current ORCA decision state.
 *
 * The exact endpoint will be replaced with the
 * endpoint agreed upon by the backend team.
 */
export async function getDecisionState() {
  return request("/api/decision-state");
}


/*
 * Get the latest candidate information.
 */
export async function getCandidates() {
  return request("/api/candidates");
}


/*
 * Get the latest hazard information.
 */
export async function getHazards() {
  return request("/api/hazards");
}


/*
 * Get the latest evidence used by the decision engine.
 */
export async function getEvidence(candidateId) {
  return request(
    `/api/evidence/${candidateId}`
  );
}


/*
 * Health check for the backend.
 */
export async function checkBackendHealth() {
  return request("/api/health");
}