/*
 * M2 → M3 ADAPTER
 *
 * Converts the M2 AgentResponse into a frontend-friendly
 * structure without recreating M2 decision logic.
 *
 * IMPORTANT:
 * We do not invent scores when M2 does not provide them.
 */

function confidenceToPercent(confidence) {
  if (confidence === null || confidence === undefined) {
    return null;
  }

  return Math.round(confidence * 100);
}

function normalizeCandidate(candidate, status) {
  if (!candidate) {
    return null;
  }

  return {
    id: candidate.pfz_id,
    name: candidate.pfz_id,

    status,

    lat: candidate.latitude,
    lng: candidate.longitude,

    distance: candidate.distance_km,

    opportunityStatus: candidate.status,

    opportunityScore:
      candidate.opportunity_score ?? null,

    confidence:
      confidenceToPercent(candidate.confidence),

    source: candidate.source ?? null,
  };
}

function normalizeEvidence(evidence) {
  if (!evidence) {
    return [];
  }

  /*
   * M2 currently returns evidence as an object keyed
   * by parameter name.
   *
   * Convert it into an array for easier rendering.
   */
  if (Array.isArray(evidence)) {
    return evidence;
  }

  return Object.entries(evidence).map(
    ([parameter, item]) => ({
      id: parameter,
      parameter: item.parameter ?? parameter,
      source: item.source ?? null,
      timestamp: item.timestamp ?? null,
      confidence:
        confidenceToPercent(item.confidence),
    })
  );
}

export function adaptM2Response(response) {
  if (!response) {
    throw new Error("M2 response is missing");
  }

  const data = response.data ?? {};

  const recommendation =
    data.pfz_recommendation ?? {};

  const recommended =
    normalizeCandidate(
      recommendation.recommended,
      "RECOMMENDED"
    );

  const alternatives =
    (recommendation.alternatives ?? [])
      .map((candidate) =>
        normalizeCandidate(
          candidate,
          "ALTERNATIVE"
        )
      );

  const rejected =
    (recommendation.rejected ?? [])
      .map((candidate) =>
        normalizeCandidate(
          candidate,
          "REJECTED"
        )
      );

  const candidates = [
    ...(recommended ? [recommended] : []),
    ...alternatives,
    ...rejected,
  ];

  const mapCoordinates =
    (data.pfz ?? []).map((candidate) => ({
      id: candidate.pfz_id,
      lat: candidate.latitude,
      lng: candidate.longitude,
    }));

  return {
    status: response.status,

    agent: response.agent,

    location: response.location,

    source: response.source,

    timestamp: response.timestamp,

    confidence:
      confidenceToPercent(response.confidence),

    error: response.error ?? null,

    /*
     * M2 currently provides marine safety status,
     * not a numeric safety score.
     */
    marineConditions: {
      sst: data.sst ?? null,
      chlorophyll: data.chlorophyll ?? null,
      waveHeight: data.wave_height ?? null,
      wavePeriod: data.wave_period ?? null,
      currentSpeed: data.current_speed ?? null,
    },

    marineSafety: {
      status:
        data.marine_safety?.status ?? null,

      hazards:
        data.marine_safety?.hazards ?? [],

      reasons:
        data.marine_safety?.reasons ?? [],
    },

    uncertainty: {
      level:
        data.uncertainty?.level ?? null,

      reason:
        data.uncertainty?.reason ?? null,

      score: null,
    },

    pfz: data.pfz ?? [],

    candidates,

    recommendedCandidate: recommended,

    alternativeCandidates: alternatives,

    rejectedCandidates: rejected,

    recommendation: {
      reason:
        recommendation.reason ?? null,
    },

    evidence:
      normalizeEvidence(data.evidence),

    map: {
      coordinates: mapCoordinates,

      hazards:
        data.marine_safety?.hazards ?? [],

      boundaryResults: [],
    },
  };
}