/*
 * ORCA M3 API SERVICE
 *
 * Frontend HTTP boundary for the final M4 Decision API.
 *
 * M4 /api/v1/decision is the integration boundary
 * for the M1 + M2 decision pipeline.
 *
 * M3 does not calculate marine safety, ranking,
 * optimization, or scientific suitability here.
 *
 * This service only:
 *   1. Sends an AgentRequest to M4.
 *   2. Enforces a frontend request timeout.
 *   3. Validates the HTTP/JSON response.
 *   4. Returns the backend response to the adapter.
 */

const DEFAULT_TIMEOUT_MS = 10000;


function getEndpoint() {
  const endpoint =
    import.meta.env.VITE_ORCA_DECISION_ENDPOINT;

  if (!endpoint) {
    throw new Error(
      "ORCA M4 decision endpoint is not configured. Set VITE_ORCA_DECISION_ENDPOINT."
    );
  }

  return endpoint;
}


function validateResponseShape(
  response
) {
  if (
    !response ||
    typeof response !== "object"
  ) {
    throw new Error(
      "Backend response is malformed."
    );
  }

  if (
    typeof response.status !== "string"
  ) {
    throw new Error(
      "Backend response is missing a valid status."
    );
  }

  return response;
}


export async function requestDecision(
  request
) {
  const endpoint =
    getEndpoint();

  const controller =
    new AbortController();

  const timeoutId =
    setTimeout(
      () => {
        controller.abort();
      },
      DEFAULT_TIMEOUT_MS
    );


  try {
    const response =
      await fetch(
        endpoint,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify(
              request
            ),

          signal:
            controller.signal,
        }
      );


    let payload;

    try {
      payload =
        await response.json();

    } catch (error) {
      throw new Error(
        "Backend returned invalid JSON.",
        {
          cause: error,
        }
      );
    }


    if (!response.ok) {
      const backendMessage =
        payload?.detail ??
        payload?.error ??
        payload?.message ??
        `Backend request failed with HTTP ${response.status}.`;

      throw new Error(
        typeof backendMessage === "string"
          ? backendMessage
          : `Backend request failed with HTTP ${response.status}.`
      );
    }


    return validateResponseShape(
      payload
    );

  } catch (error) {

    if (
      error?.name ===
      "AbortError"
    ) {
      throw new Error(
        "ORCA M4 decision backend request timed out after 10 seconds.",
        {
          cause: error,
        }
      );
    }

    if (
      error instanceof TypeError
    ) {
      throw new Error(
        "Unable to reach the ORCA M4 decision backend.",
        {
          cause: error,
        }
      );
    }

    throw error;

  } finally {

    clearTimeout(
      timeoutId
    );

  }
}


/*
 * Legacy name retained only for compatibility.
 *
 * It now points to the final M4 decision request.
 * It does NOT fall back to the old M2 endpoint.
 */
export async function requestOceanData(
  request
) {
  return requestDecision(
    request
  );
}