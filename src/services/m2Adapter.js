/*
 * M2 → M3 ADAPTER
 *
 * Converts backend responses into a frontend-friendly
 * structure without recreating marine safety, ranking,
 * optimization, or decision logic.
 *
 * IMPORTANT:
 * M3 only displays decision information supplied
 * by the backend.
 */

import {
  adaptGISData,
} from "./gisAdapter.js";


const DECISION_STATES = new Set([
  "RECOMMENDED",
  "ALTERNATIVE",
  "UNSAFE",
  "INSUFFICIENT_EVIDENCE",
  "DOMINATED",
  "REJECTED",
]);


function confidenceToPercent(
  confidence
) {
  if (
    confidence === null ||
    confidence === undefined
  ) {
    return null;
  }

  if (
    typeof confidence !== "number"
  ) {
    return null;
  }

  return Math.round(
    confidence * 100
  );
}


function confidenceToUncertaintyPercent(
  confidence
) {
  if (
    confidence === null ||
    confidence === undefined
  ) {
    return null;
  }

  if (
    typeof confidence !== "number"
  ) {
    return null;
  }

  return Math.round(
    (1 - confidence) * 100
  );
}


function getSemanticState(
  candidate,
  fallbackStatus
) {
  const suppliedState =
    candidate?.decision_status ??
    candidate?.semantic_status ??
    candidate?.decisionState ??
    candidate?.decision_state ??
    null;

  if (
    typeof suppliedState === "string"
  ) {
    const normalized =
      suppliedState
        .trim()
        .toUpperCase()
        .replace(
          /[\s-]+/g,
          "_"
        );

    if (
      DECISION_STATES.has(
        normalized
      )
    ) {
      return normalized;
    }
  }

  return fallbackStatus;
}


function normalizeCandidate(
  candidate,
  fallbackStatus
) {
  if (!candidate) {
    return null;
  }

  return {
    id:
      candidate.pfz_id ??
      candidate.id ??
      null,

    name:
      candidate.name ??
      candidate.pfz_id ??
      candidate.id ??
      "Unnamed candidate",

    status:
      getSemanticState(
        candidate,
        fallbackStatus
      ),

    lat:
      candidate.latitude ??
      candidate.lat ??
      null,

    lng:
      candidate.longitude ??
      candidate.lng ??
      null,

    distance:
      candidate.distance_km ??
      candidate.distance ??
      null,

    opportunityStatus:
      candidate.opportunity_status ??
      candidate.status ??
      null,

    opportunityScore:
      candidate.opportunity_score ??
      null,

    confidence:
      confidenceToPercent(
        candidate.confidence
      ),

    source:
      candidate.source ??
      null,

    reason:
      candidate.reason ??
      candidate.rejection_reason ??
      null,

    rejectionReason:
      candidate.rejection_reason ??
      candidate.rejectionReason ??
      null,

    rejectionReasons:
      Array.isArray(
        candidate.rejection_reasons
      )
        ? candidate.rejection_reasons
        : [],

    informationGaps:
      Array.isArray(
        candidate.information_gaps
      )
        ? candidate.information_gaps
        : [],
  };
}


function normalizeEvidence(
  evidence
) {
  if (!evidence) {
    return [];
  }

  if (
    Array.isArray(evidence)
  ) {
    return evidence;
  }

  if (
    typeof evidence !== "object"
  ) {
    return [];
  }

  return Object.entries(
    evidence
  ).map(
    ([parameter, item]) => ({
      id:
        parameter,

      parameter:
        item?.parameter ??
        parameter,

      source:
        item?.source ??
        null,

      timestamp:
        item?.timestamp ??
        null,

      confidence:
        confidenceToPercent(
          item?.confidence
        ),

      value:
        item?.value ??
        null,

      observation:
        item?.observation ??
        null,
    })
  );
}


function normalizeArray(
  value
) {
  return Array.isArray(value)
    ? value
    : [];
}


function normalizeAnalysis(
  value
) {
  if (
    value === null ||
    value === undefined
  ) {
    return null;
  }

  if (
    typeof value !== "object"
  ) {
    return null;
  }

  return value;
}


export function adaptM2Response(
  response
) {
  if (!response) {
    throw new Error(
      "M2 response is missing."
    );
  }


  if (
    typeof response !== "object"
  ) {
    throw new Error(
      "Backend response is malformed."
    );
  }


  const data =
    response.data ?? {};


  if (
    typeof data !== "object"
  ) {
    throw new Error(
      "Backend response data is malformed."
    );
  }


  const recommendation =
    data.pfz_recommendation ??
    {};


  if (
    typeof recommendation !== "object"
  ) {
    throw new Error(
      "PFZ recommendation data is malformed."
    );
  }


  const recommended =
    normalizeCandidate(
      recommendation.recommended,
      "RECOMMENDED"
    );


  const alternatives =
    normalizeArray(
      recommendation.alternatives
    ).map(
      (candidate) =>
        normalizeCandidate(
          candidate,
          "ALTERNATIVE"
        )
    );


  const rejected =
    normalizeArray(
      recommendation.rejected
    ).map(
      (candidate) =>
        normalizeCandidate(
          candidate,
          "REJECTED"
        )
    );


  const candidates = [
    ...(recommended
      ? [recommended]
      : []),

    ...alternatives,

    ...rejected,
  ];


  const pfz =
    normalizeArray(
      data.pfz
    );


  const mapCoordinates =
    pfz
      .map(
        (candidate) => ({
          id:
            candidate.pfz_id ??
            candidate.id ??
            null,

          lat:
            candidate.latitude ??
            candidate.lat ??
            null,

          lng:
            candidate.longitude ??
            candidate.lng ??
            null,
        })
      )
      .filter(
        (candidate) =>
          typeof candidate.lat === "number" &&
          typeof candidate.lng === "number"
      );


  const uncertaintyScore =
    confidenceToUncertaintyPercent(
      response.confidence
    );


  const marineSafety =
    data.marine_safety ?? {};


  const backendUncertainty =
    marineSafety.uncertainty ??
    {};


  const sensitivity =
    normalizeAnalysis(
      data.sensitivity ??
      response.sensitivity
    );


  const counterfactual =
    normalizeAnalysis(
      data.counterfactual ??
      data.counterfactual_results ??
      response.counterfactual ??
      response.counterfactual_results
    );


  const robustness =
    normalizeAnalysis(
      data.robustness ??
      response.robustness
    );


  const informationGaps =
    normalizeArray(
      data.information_gaps ??
      response.information_gaps
    );


  const gis =
    adaptGISData(
      data.gis ??
      data.gis_data ??
      response.gis ??
      response.gis_data
    );


  return {

    status:
      response.status ??
      null,

    agent:
      response.agent ??
      null,

    location:
      response.location ??
      null,

    source:
      response.source ??
      null,

    timestamp:
      response.timestamp ??
      null,

    confidence:
      confidenceToPercent(
        response.confidence
      ),

    error:
      response.error ??
      null,


    marineConditions: {

      sst:
        data.sst ??
        null,

      chlorophyll:
        data.chlorophyll ??
        null,

      waveHeight:
        data.wave_height ??
        null,

      wavePeriod:
        data.wave_period ??
        null,

      currentSpeed:
        data.current_speed ??
        null,
    },


    marineSafety: {

      status:
        marineSafety.status ??
        null,

      hazards:
        normalizeArray(
          marineSafety.hazards
        ),

      reasons:
        normalizeArray(
          marineSafety.reasons
        ),
    },


    uncertainty: {

      level:
        backendUncertainty.level ??
        null,

      reason:
        backendUncertainty.reason ??
        null,

      score:
        uncertaintyScore,
    },


    pfz,

    candidates,

    recommendedCandidate:
      recommended,

    alternativeCandidates:
      alternatives,

    rejectedCandidates:
      rejected,


    recommendation: {

      reason:
        recommendation.reason ??
        null,
    },


    evidence:
      normalizeEvidence(
        data.evidence
      ),


    sensitivity,

    counterfactual,

    robustness,

    informationGaps,


    gis,


    map: {

      coordinates:
        mapCoordinates,

      hazards:
        normalizeArray(
          marineSafety.hazards
        ),

      boundaryResults:
        [],
    },


    decisionMetadata: {

      authoritative:
        false,

      contract:
        "M2 AgentResponse",

      note:
        "M2 response is displayed as supplied. M3 does not recreate decision intelligence.",

    },

  };
}