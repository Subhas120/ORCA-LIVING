/*
 * ORCA M3 DECISION SERVICE
 *
 * This is the integration layer between the
 * frontend and the M2 Ocean Agent response.
 *
 * api.js
 *   ↓
 * raw backend response
 *
 * m2Adapter.js
 *   ↓
 * normalized M3 decision state
 *
 * React components
 *   ↓
 * visualization
 */

import {
  requestOceanData,
} from "./api.js";

import {
  adaptM2Response,
} from "./m2Adapter.js";


/*
 * Get an ORCA decision from the backend.
 *
 * The request follows the shared AgentRequest
 * structure provided by M1/M2.
 */
export async function getDecision(
  request
) {
  const m2Response =
    await requestOceanData(request);

  return adaptM2Response(
    m2Response
  );
}