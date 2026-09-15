/*
 * ORCA M3 DECISION SERVICE
 *
 * M3 communicates with the authoritative M4 integration API.
 *
 * M4
 *  ↓
 * /api/v1/decision
 *  ↓
 * M4 response
 *  ↓
 * m4Adapter
 *  ↓
 * M3 visualization
 */

import { requestDecision } from "./api.js";

import {
  adaptM4Response,
} from "./m4Adapter.js";

export async function getDecision(request) {
  const m4Response = await requestDecision(request);

  return adaptM4Response(m4Response);
}