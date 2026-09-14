/*
 * ORCA M4 RESPONSE ADAPTER
 *
 * Converts the authoritative M4 /api/v1/decision response
 * into the normalized shape expected by the existing M3 UI.
 *
 * M4 owns the decision.
 * M3 only visualizes it.
 */

export function adaptM4Response(response) {
  const recommended = response.recommendedCandidate ?? null;

  const alternatives = response.alternativeCandidates ?? [];
  const rejected = response.rejectedCandidates ?? [];

  const candidates = [
    ...(recommended ? [recommended] : []),
    ...alternatives,
    ...rejected,
  ];

  const parsePercentage = (value) => {
    if (value == null) {
      return null;
    }

    const parsed = Number.parseInt(
      String(value).replace("%", ""),
      10,
    );

    return Number.isFinite(parsed) ? parsed : null;
  };

  return {
    /*
     * ---------------------------------------------------------
     * Authoritative M4 decision status
     * ---------------------------------------------------------
     */
    status: response.status,

    /*
     * ---------------------------------------------------------
     * User objective
     *
     * Prefer the actual M4 response.
     * ---------------------------------------------------------
     */
    objective: response.objective ?? null,

    /*
     * ---------------------------------------------------------
     * Decision confidence
     *
     * This is M1's confidence when available.
     * Do not derive decision confidence from safety.
     * ---------------------------------------------------------
     */
    confidence:
      response.confidence != null
        ? parsePercentage(response.confidence)
        : recommended?.confidence != null
          ? parsePercentage(recommended.confidence)
          : null,

    /*
     * ---------------------------------------------------------
     * Recommendation
     * ---------------------------------------------------------
     */
    recommendation: recommended
      ? {
        id: recommended.id,
        name: recommended.name,
        reason:
          recommended.reason ??
          response.decisionSummary ??
          "Recommendation reason unavailable.",
      }
      : null,

    /*
     * ---------------------------------------------------------
     * Recommended candidate
     * ---------------------------------------------------------
     */
    recommendedCandidate: recommended
      ? {
        id: recommended.id,
        name: recommended.name,
        status: recommended.status,

        /*
         * Safety is intentionally not reconstructed here.
         * Authoritative marine safety comes from M4.
         */
        safety: recommended.safety ?? null,

        opportunity:
          recommended.opportunity ?? null,

        uncertainty:
          recommended.uncertainty ?? null,

        distance:
          recommended.distance ?? null,

        confidence:
          parsePercentage(
            recommended.confidence,
          ),

        lat: recommended.lat,
        lng: recommended.lng,

        reason:
          recommended.reason ??
          response.decisionSummary ??
          null,
      }
      : null,

    /*
     * ---------------------------------------------------------
     * All candidates
     *
     * Candidate status comes directly from M4.
     * M3 does not reclassify candidates.
     * ---------------------------------------------------------
     */
    candidates: candidates.map((candidate) => ({
      id: candidate.id,
      name: candidate.name,
      status: candidate.status,

      safety: candidate.safety ?? null,

      opportunity:
        candidate.opportunity ?? null,

      uncertainty:
        candidate.uncertainty ?? null,

      distance:
        candidate.distance ?? null,

      confidence:
        parsePercentage(
          candidate.confidence,
        ),

      lat: candidate.lat,
      lng: candidate.lng,

      reason:
        candidate.reason ?? null,

      opportunityStatus: null,
    })),

    /*
     * ---------------------------------------------------------
     * AUTHORITATIVE MARINE SAFETY
     *
     * This MUST come directly from M4.
     *
     * Do NOT derive safety from:
     *   candidate.status
     *   candidate.safety
     *   opportunity
     *   confidence
     * ---------------------------------------------------------
     */
    marineSafety: {
      status:
        response.marineSafetyStatus ??
        "UNKNOWN",

      reasons:
        response.marineSafetyReasons ?? [],
    },

    /*
     * ---------------------------------------------------------
     * Marine conditions
     *
     * M4 currently does not expose a conditions object.
     * ---------------------------------------------------------
     */
    marineConditions:
      response.marineConditions ?? null,

    /*
     * ---------------------------------------------------------
     * Uncertainty
     *
     * Preserve the actual M4 object.
     * Never fabricate an uncertainty value.
     * ---------------------------------------------------------
     */
    uncertainty:
      response.uncertainty ?? null,

    /*
     * ---------------------------------------------------------
     * Evidence
     * ---------------------------------------------------------
     */
    evidence:
      response.evidence ?? [],

    /*
     * ---------------------------------------------------------
     * Tradeoffs
     * ---------------------------------------------------------
     */
    tradeoffs:
      response.tradeoffs ?? [],

    /*
     * ---------------------------------------------------------
     * Sensitivity
     * ---------------------------------------------------------
     */
    sensitivity:
      response.sensitivity ?? null,

    /*
     * ---------------------------------------------------------
     * M1 Decision Intelligence
     *
     * Preserve the fields supplied by M4.
     * M3 does not calculate them.
     * ---------------------------------------------------------
     */
    paretoCandidateIds:
      response.paretoCandidateIds ?? [],

    robustness:
      response.robustness ?? null,

    valueOfInformation:
      response.valueOfInformation ?? null,

    counterfactuals:
      response.counterfactuals ?? [],

    explanation:
      response.explanation ?? null,

    decisionTrace:
      response.decisionTrace ?? null,

    /*
     * ---------------------------------------------------------
     * Decision summary
     * ---------------------------------------------------------
     */
    decisionSummary:
      response.decisionSummary ??
      "No decision summary available.",

    /*
     * ---------------------------------------------------------
     * Explicit rejected candidates
     *
     * These are M4/M1 classifications.
     * Never convert them into alternatives.
     * ---------------------------------------------------------
     */
    rejectedCandidates:
      rejected,

    /*
     * ---------------------------------------------------------
     * Data mode
     * ---------------------------------------------------------
     */
    dataMode:
      response.dataMode ?? "DEMO",
  };
}