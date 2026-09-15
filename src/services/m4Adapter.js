/*
 * ORCA M4 RESPONSE ADAPTER
 *
 * Converts the authoritative M4 /api/v1/decision response
 * into the normalized shape expected by the existing M3 UI.
 *
 * M4 owns the decision.
 * M3 only visualizes it.
 *
 * Important:
 * M3 does not derive decision confidence, uncertainty,
 * safety, ranking, optimization, Pareto results, or
 * scientific suitability from other fields.
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
    status: response.status,
    objective: response.objective ?? null,

    /*
     * Decision-level confidence is displayed only when M4
     * explicitly supplies a top-level confidence field.
     *
     * Do NOT derive it from recommendedCandidate.confidence.
     */
    confidence:
      response.confidence != null
        ? parsePercentage(response.confidence)
        : null,

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

    recommendedCandidate: recommended
      ? {
        id: recommended.id,
        name: recommended.name,
        status: recommended.status,
        safety: recommended.safety ?? null,
        opportunity: recommended.opportunity ?? null,
        uncertainty: recommended.uncertainty ?? null,
        distance: recommended.distance ?? null,
        confidence: parsePercentage(recommended.confidence),
        lat: recommended.lat,
        lng: recommended.lng,
        reason:
          recommended.reason ??
          response.decisionSummary ??
          null,
      }
      : null,

    candidates: candidates.map((candidate) => ({
      id: candidate.id,
      name: candidate.name,
      status: candidate.status,
      safety: candidate.safety ?? null,
      opportunity: candidate.opportunity ?? null,
      uncertainty: candidate.uncertainty ?? null,
      distance: candidate.distance ?? null,
      confidence: parsePercentage(candidate.confidence),
      lat: candidate.lat,
      lng: candidate.lng,
      reason: candidate.reason ?? null,
      opportunityStatus: null,
    })),

    /*
     * Safety is authoritative only when supplied by M4.
     * UNKNOWN means M4 did not provide a marine safety status.
     */
    marineSafety: {
      status: response.marineSafetyStatus ?? "UNKNOWN",
      reasons: response.marineSafetyReasons ?? [],
    },

    marineConditions: response.marineConditions ?? null,

    /*
     * Never derive uncertainty from candidate confidence.
     */
    uncertainty: response.uncertainty ?? null,

    evidence: response.evidence ?? [],
    tradeoffs: response.tradeoffs ?? [],
    sensitivity: response.sensitivity ?? null,

    /*
     * These fields are passed through only if M4 supplies them.
     * M3 does not calculate them locally.
     */
    paretoCandidateIds: response.paretoCandidateIds ?? [],
    robustness: response.robustness ?? null,
    valueOfInformation: response.valueOfInformation ?? null,
    counterfactuals: response.counterfactuals ?? [],
    explanation: response.explanation ?? null,
    decisionTrace: response.decisionTrace ?? null,

    decisionSummary:
      response.decisionSummary ??
      "No decision summary available.",

    rejectedCandidates: rejected,

    dataMode: response.dataMode ?? "UNKNOWN",
  };
}