/*
 * ORCA M3 DECISION SERVICE
 *
 * Integration flow:
 *
 * M3 frontend
 *     ↓
 * M4 /api/v1/decision
 *     ↓
 * M1 + M2 decision pipeline
 *     ↓
 * M4 DecisionResponse
 *     ↓
 * M3 response adapter
 *
 * M3 only consumes and visualizes the supplied
 * decision information.
 */

import {
  requestDecision,
} from "./api.js";

import {
  adaptDecisionResponse,
} from "./m2Adapter.js";


/*
 * Get the final ORCA decision from the
 * M4 decision integration endpoint.
 */
export async function getDecision(
  request
) {
  const backendResponse =
    await requestDecision(
      request
    );

  return adaptDecisionResponse(
    backendResponse
  );
}