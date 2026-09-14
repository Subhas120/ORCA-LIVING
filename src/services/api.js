/*
 * ORCA M3 API SERVICE
 *
 * Frontend HTTP boundary for the M2 Ocean API.
 *
 * M3 does not calculate marine safety, ranking,
 * optimization, or scientific suitability here.
 *
 * This service only:
 *   1. Sends an AgentRequest to the backend.
 *   2. Enforces a frontend request timeout.
 *   3. Validates the basic HTTP/JSON response shape.
 *   4. Returns the backend response to the M2 adapter.
 */

const DEFAULT_TIMEOUT_MS = 10000;


function getEndpoint() {
  const endpoint =
    import.meta.env.VITE_ORCA_OCEAN_ENDPOINT;

  if (!endpoint) {
    throw new Error(
      "ORCA backend endpoint is not configured."
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

  if (
    response.data !== undefined &&
    (
      response.data === null ||
      typeof response.data !== "object"
    )
  ) {
    throw new Error(
      "Backend response data is malformed."
    );
  }

  return response;
}


export async function requestOceanData(
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
        payload?.error ??
        payload?.message ??
        `Backend request failed with HTTP ${response.status}.`;

      throw new Error(
        backendMessage
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
        "ORCA backend request timed out after 10 seconds.",
        {
          cause: error,
        }
      );
    }

    if (
      error instanceof TypeError
    ) {
      throw new Error(
        "Unable to reach the ORCA backend.",
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