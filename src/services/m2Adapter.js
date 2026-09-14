/*
 * ORCA DECISION RESPONSE ADAPTER
 *
 * Converts the final M4 DecisionResponse into
 * the normalized structure consumed by M3.
 *
 * M4 is the integration boundary for the
 * M1 + M2 decision pipeline.
 *
 * IMPORTANT:
 * M3 displays supplied decision semantics.
 * It does not recreate safety, ranking,
 * optimization, dominance, or scientific logic.
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


/*
 * Normalize confidence values without inventing
 * or transforming missing information.
 *
 * Supported backend forms:
 *   0.91     -> 91
 *   91       -> 91
 *   "91%"    -> 91
 *   "91"     -> 91
 */
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
    typeof confidence === "number"
  ) {
    if (
      confidence >= 0 &&
      confidence <= 1
    ) {
      return Math.round(
        confidence * 100
      );
    }

    return Math.round(
      confidence
    );
  }

  if (
    typeof confidence === "string"
  ) {
    const trimmed =
      confidence.trim();

    if (!trimmed) {
      return null;
    }

    const numeric =
      Number(
        trimmed.replace(
          "%",
          ""
        )
      );

    if (
      Number.isFinite(
        numeric
      )
    ) {
      return Math.round(
        numeric
      );
    }

    return trimmed;
  }

  return null;
}


/*
 * Opportunity is a separate semantic field.
 *
 * M4 supplies opportunity as an integer score.
 * M3 must display it directly and must not
 * derive it from status or confidence.
 */
function opportunityToScore(
  opportunity
) {
  if (
    opportunity === null ||
    opportunity === undefined
  ) {
    return null;
  }

  if (
    typeof opportunity === "number"
  ) {
    return Number.isFinite(
      opportunity
    )
      ? opportunity
      : null;
  }

  if (
    typeof opportunity === "string"
  ) {
    const numeric =
      Number(
        opportunity.replace(
          "%",
          ""
        ).trim()
      );

    return Number.isFinite(
      numeric
    )
      ? numeric
      : null;
  }

  return null;
}


function normalizeState(
  state,
  fallback
) {
  if (
    typeof state !== "string"
  ) {
    return fallback;
  }

  const normalized =
    state
      .trim()
      .toUpperCase()
      .replace(
        /[\s-]+/g,
        "_"
      );

  return DECISION_STATES.has(
    normalized
  )
    ? normalized
    : fallback;
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
      candidate.id ??
      candidate.pfz_id ??
      null,

    name:
      candidate.name ??
      candidate.id ??
      candidate.pfz_id ??
      "Unnamed candidate",

    status:
      normalizeState(
        candidate.status ??
        candidate.decision_status ??
        candidate.semantic_status,
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

    /*
     * Preserve both the semantic opportunity
     * status and the actual numeric opportunity
     * score when supplied by M4.
     */
    opportunityStatus:
      candidate.opportunity_status ??
      null,

    opportunityScore:
      opportunityToScore(
        candidate.opportunity ??
        candidate.opportunity_score ??
        candidate.expected_opportunity
      ),

    opportunity:
      opportunityToScore(
        candidate.opportunity ??
        candidate.opportunity_score ??
        candidate.expected_opportunity
      ),

    confidence:
      confidenceToPercent(
        candidate.confidence
      ),

    /*
     * Safety is deliberately passed through only
     * when the authoritative candidate contains it.
     * M3 never derives safety locally.
     */
    safety:
      candidate.safety ??
      null,

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


function normalizeCandidateArray(
  candidates,
  fallbackStatus
) {
  if (
    !Array.isArray(
      candidates
    )
  ) {
    return [];
  }

  return candidates
    .map(
      (candidate) =>
        normalizeCandidate(
          candidate,
          fallbackStatus
        )
    )
    .filter(
      Boolean
    );
}


function normalizeEvidence(
  evidence
) {
  if (!evidence) {
    return [];
  }

  if (
    Array.isArray(
      evidence
    )
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
        item?.id ??
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
  return Array.isArray(
    value
  )
    ? value
    : [];
}


function normalizeObject(
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


function adaptDecisionIntelligence(
  response
) {
  const intelligence =
    response.decision_intelligence ??
    response.decisionIntelligence ??
    response.decision ??
    null;

  if (
    !intelligence ||
    typeof intelligence !== "object"
  ) {
    return null;
  }

  return {
    recommendedCandidate:
      intelligence.recommended_candidate ??
      intelligence.recommendedCandidate ??
      null,

    alternativeCandidates:
      normalizeArray(
        intelligence.alternative_candidates ??
        intelligence.alternativeCandidates
      ),

    rejectedCandidates:
      normalizeArray(
        intelligence.rejected_candidates ??
        intelligence.rejectedCandidates
      ),

    rejectionReasons:
      normalizeArray(
        intelligence.rejection_reasons ??
        intelligence.rejectionReasons
      ),

    paretoPoints:
      normalizeArray(
        intelligence.pareto_points ??
        intelligence.paretoPoints
      ),

    tradeoffs:
      normalizeArray(
        intelligence.tradeoffs
      ),

    evidenceRefs:
      normalizeArray(
        intelligence.evidence_refs ??
        intelligence.evidenceRefs
      ),

    uncertaintyRefs:
      normalizeArray(
        intelligence.uncertainty_refs ??
        intelligence.uncertaintyRefs
      ),

    robustness:
      normalizeObject(
        intelligence.robustness
      ),

    sensitivity:
      normalizeObject(
        intelligence.sensitivity
      ),

    valueOfInformation:
      normalizeObject(
        intelligence.value_of_information ??
        intelligence.valueOfInformation
      ),

    counterfactuals:
      normalizeArray(
        intelligence.counterfactuals
      ),

    explanation:
      intelligence.explanation ??
      null,

    decisionTrace:
      normalizeArray(
        intelligence.decision_trace ??
        intelligence.decisionTrace
      ),

    confidence:
      confidenceToPercent(
        intelligence.confidence
      ),

    summary:
      intelligence.summary ??
      null,
  };
}


function adaptAuthoritativeCandidates(
  response,
  intelligence
) {
  const recommended =
    normalizeCandidate(
      response.recommended_candidate ??
      response.recommendedCandidate ??
      intelligence?.recommendedCandidate,
      "RECOMMENDED"
    );

  const alternatives =
    normalizeCandidateArray(
      response.alternative_candidates ??
      response.alternativeCandidates ??
      intelligence?.alternativeCandidates,
      "ALTERNATIVE"
    );

  const rejected =
    normalizeCandidateArray(
      response.rejected_candidates ??
      response.rejectedCandidates ??
      intelligence?.rejectedCandidates,
      "REJECTED"
    );

  return {
    recommended,
    alternatives,
    rejected,
    candidates: [
      ...(recommended
        ? [recommended]
        : []),
      ...alternatives,
      ...rejected,
    ],
  };
}


export function adaptDecisionResponse(
  response
) {
  if (!response) {
    throw new Error(
      "Decision response is missing."
    );
  }

  if (
    typeof response !== "object"
  ) {
    throw new Error(
      "Decision response is malformed."
    );
  }

  if (
    typeof response.status !== "string"
  ) {
    throw new Error(
      "Decision response is missing a valid status."
    );
  }

  const intelligence =
    adaptDecisionIntelligence(
      response
    );

  const candidateState =
    adaptAuthoritativeCandidates(
      response,
      intelligence
    );

  /*
   * IMPORTANT:
   * Uncertainty is authoritative only when
   * the backend actually supplies it.
   *
   * Never calculate:
   *   uncertainty = 100 - confidence
   */
  const uncertainty =
    normalizeObject(
      response.uncertainty
    ) ??
    null;

  const sensitivity =
    normalizeObject(
      response.sensitivity
    ) ??
    intelligence?.sensitivity ??
    null;

  const robustness =
    normalizeObject(
      response.robustness
    ) ??
    intelligence?.robustness ??
    null;

  const counterfactual =
    normalizeObject(
      response.counterfactual ??
      response.counterfactual_results
    );

  const informationGaps =
    normalizeArray(
      response.information_gaps ??
      response.informationGaps
    );

  const evidence =
    normalizeEvidence(
      response.evidence ??
      response.evidence_links
    );

  const gis =
    adaptGISData(
      response.gis ??
      response.gis_data
    );

  const confidence =
    confidenceToPercent(
      response.confidence ??
      intelligence?.confidence ??
      response.recommendedCandidate?.confidence ??
      response.recommended_candidate?.confidence
    );

  const decisionStatus =
    response.status ??
    null;

  const marineSafety =
    response.marine_safety ??
    response.marineSafety ??
    {};

  return {
    status:
      decisionStatus,

    agent:
      response.agent ??
      "decision",

    location:
      response.location ??
      null,

    source:
      response.source ??
      null,

    timestamp:
      response.timestamp ??
      null,

    /*
     * Preserve the backend data mode.
     *
     * M3 must not reinterpret DEMO as LIVE.
     */
    dataMode:
      response.dataMode ??
      response.data_mode ??
      "UNKNOWN",

    confidence,

    error:
      response.error ??
      null,

    marineConditions:
      response.marine_conditions ??
      response.marineConditions ??
      {
        sst: null,
        chlorophyll: null,
        waveHeight: null,
        wavePeriod: null,
        currentSpeed: null,
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

    /*
     * No fallback from confidence.
     * If M4 does not supply uncertainty,
     * the UI receives null and can display
     * NOT SUPPLIED.
     */
    uncertainty: {
      level:
        uncertainty?.level ??
        null,

      reason:
        uncertainty?.reason ??
        uncertainty?.explanation ??
        null,

      score:
        uncertainty?.score !== undefined &&
        uncertainty?.score !== null
          ? confidenceToPercent(
              uncertainty.score
            )
          : null,
    },

    pfz:
      normalizeArray(
        response.pfz
      ),

    candidates:
      candidateState.candidates,

    recommendedCandidate:
      candidateState.recommended,

    alternativeCandidates:
      candidateState.alternatives,

    rejectedCandidates:
      candidateState.rejected,

    recommendation: {
      reason:
        response.decision_summary ??
        response.decisionSummary ??
        intelligence?.summary ??
        null,
    },

    decisionSummary:
      response.decision_summary ??
      response.decisionSummary ??
      intelligence?.summary ??
      null,

    tradeoffs:
      normalizeArray(
        response.tradeoffs ??
        intelligence?.tradeoffs
      ),

    evidence,

    sensitivity,

    counterfactual,

    robustness,

    informationGaps,

    decisionIntelligence:
      intelligence,

    gis,

    map: {
      coordinates:
        candidateState.candidates
          .map(
            (candidate) => ({
              id:
                candidate.id,

              lat:
                candidate.lat,

              lng:
                candidate.lng,
            })
          )
          .filter(
            (candidate) =>
              typeof candidate.lat === "number" &&
              typeof candidate.lng === "number"
          ),

      hazards:
        normalizeArray(
          marineSafety.hazards
        ),

      boundaryResults:
        [],
    },

    decisionMetadata: {
      authoritative:
        true,

      contract:
        "M4 DecisionResponse",

      note:
        "Decision information is displayed from the final M4 integration response. M3 does not recreate decision intelligence.",
    },
  };
}


/*
 * Backward-compatible adapter for the older
 * M2 AgentResponse.
 *
 * Kept temporarily so existing imports do not
 * break while the final M4 contract is adopted.
 */
export function adaptM2Response(
  response
) {
  if (
    response?.data?.pfz_recommendation
  ) {
    const data =
      response.data;

    const recommendation =
      data.pfz_recommendation ??
      {};

    const adapted =
      adaptDecisionResponse({
        status:
          response.status ??
          "success",

        agent:
          response.agent ??
          "ocean",

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
          response.confidence ??
          null,

        recommended_candidate:
          recommendation.recommended,

        alternative_candidates:
          recommendation.alternatives,

        rejected_candidates:
          recommendation.rejected,

        decision_summary:
          recommendation.reason,

        evidence:
          data.evidence,

        pfz:
          data.pfz,

        marine_safety:
          data.marine_safety,

        sensitivity:
          data.sensitivity,

        counterfactual:
          data.counterfactual,

        robustness:
          data.robustness,

        information_gaps:
          data.information_gaps,

        dataMode:
          response.dataMode ??
          response.data_mode ??
          "UNKNOWN",
      });

    return {
      ...adapted,

      decisionMetadata: {
        authoritative:
          false,

        contract:
          "M2 AgentResponse",

        note:
          "Legacy M2 response displayed for backward compatibility. Final M3 runtime should use M4 DecisionResponse.",
      },
    };
  }

  return adaptDecisionResponse(
    response
  );
}