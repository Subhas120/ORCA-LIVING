/*
 * M2 → M3 ADAPTER
 *
 * Converts the M2 AgentResponse into a frontend-friendly
 * structure without recreating M2 decision logic.
 *
 * IMPORTANT:
 * We do not invent decision scores.
 *
 * The uncertainty score shown by M3 is derived from
 * the confidence value supplied by M2:
 *
 * M2 confidence 0.85
 * →
 * M3 uncertainty 15%
 *
 * This is a presentation-level conversion only.
 */


function confidenceToPercent(confidence) {
  if (
    confidence === null ||
    confidence === undefined
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

  return Math.round(
    (1 - confidence) * 100
  );
}


function normalizeCandidate(
  candidate,
  status
) {
  if (!candidate) {
    return null;
  }

  return {
    id: candidate.pfz_id,

    name: candidate.pfz_id,

    status,

    lat: candidate.latitude,

    lng: candidate.longitude,

    distance:
      candidate.distance_km,

    opportunityStatus:
      candidate.status,

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
  };
}


function normalizeEvidence(
  evidence
) {
  if (!evidence) {
    return [];
  }

  /*
   * M2 currently returns evidence as an object
   * keyed by parameter name.
   *
   * Convert it into an array for easier rendering.
   */

  if (Array.isArray(evidence)) {
    return evidence;
  }

  return Object.entries(
    evidence
  ).map(
    ([parameter, item]) => ({
      id: parameter,

      parameter:
        item.parameter ??
        parameter,

      source:
        item.source ??
        null,

      timestamp:
        item.timestamp ??
        null,

      confidence:
        confidenceToPercent(
          item.confidence
        ),
    })
  );
}


export function adaptM2Response(
  response
) {
  if (!response) {
    throw new Error(
      "M2 response is missing"
    );
  }


  const data =
    response.data ?? {};


  const recommendation =
    data.pfz_recommendation ??
    {};


  const recommended =
    normalizeCandidate(
      recommendation.recommended,
      "RECOMMENDED"
    );


  const alternatives =
    (
      recommendation.alternatives ??
      []
    ).map(
      (candidate) =>
        normalizeCandidate(
          candidate,
          "ALTERNATIVE"
        )
    );


  const rejected =
    (
      recommendation.rejected ??
      []
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


  const mapCoordinates =
    (data.pfz ?? []).map(
      (candidate) => ({
        id: candidate.pfz_id,

        lat:
          candidate.latitude,

        lng:
          candidate.longitude,
      })
    );


  /*
   * M2 provides an overall confidence value.
   *
   * Convert that confidence into an uncertainty
   * percentage for visualization:
   *
   * confidence 0.85
   * →
   * uncertainty 15%
   */

  const uncertaintyScore =
    confidenceToUncertaintyPercent(
      response.confidence
    );


  /*
   * M2's marine safety object contains the
   * authoritative uncertainty level/reason.
   */

  const marineSafety =
    data.marine_safety ?? {};


  const backendUncertainty =
    marineSafety.uncertainty ?? {};


  return {

    status:
      response.status,

    agent:
      response.agent,

    location:
      response.location,

    source:
      response.source,

    timestamp:
      response.timestamp,

    confidence:
      confidenceToPercent(
        response.confidence
      ),

    error:
      response.error ?? null,


    /*
     * M2 currently provides marine condition
     * values, not frontend-generated values.
     */

    marineConditions: {

      sst:
        data.sst ?? null,

      chlorophyll:
        data.chlorophyll ?? null,

      waveHeight:
        data.wave_height ?? null,

      wavePeriod:
        data.wave_period ?? null,

      currentSpeed:
        data.current_speed ?? null,
    },


    /*
     * M2 is authoritative for marine safety.
     *
     * No safety score is fabricated here.
     */

    marineSafety: {

      status:
        marineSafety.status ??
        null,

      hazards:
        marineSafety.hazards ??
        [],

      reasons:
        marineSafety.reasons ??
        [],
    },


    /*
     * Uncertainty visualization.
     *
     * Level and reason come from M2.
     *
     * Score is derived only from the M2
     * top-level confidence value.
     */

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


    pfz:
      data.pfz ?? [],


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


    map: {

      coordinates:
        mapCoordinates,

      hazards:
        marineSafety.hazards ??
        [],

      boundaryResults:
        [],
    },
  };
}