/*
 * ORCA M3 API SERVICE
 *
 * The frontend communicates with the ORCA backend
 * through this service only.
 *
 * The actual backend endpoint is supplied through:
 *
 * VITE_ORCA_OCEAN_ENDPOINT
 *
 * We do not hard-code an endpoint because the
 * M1/M2/M3 REST contract is not finalized yet.
 */

const OCEAN_ENDPOINT =
  import.meta.env.VITE_ORCA_OCEAN_ENDPOINT || null;


/*
 * Send an AgentRequest to the backend.
 *
 * Expected request structure:
 *
 * {
 *   query,
 *   location,
 *   destination,
 *   date,
 *   time,
 *   activity
 * }
 */
export async function requestOceanData(
  request
) {
  if (!OCEAN_ENDPOINT) {
    throw new Error(
      "ORCA Ocean API endpoint is not configured."
    );
  }

  const response = await fetch(
    OCEAN_ENDPOINT,
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
      `ORCA backend request failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}