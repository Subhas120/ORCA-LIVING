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

  return {
    status: response.status,

    confidence:
      recommended?.confidence != null
        ? Number.parseInt(
            String(recommended.confidence).replace("%", ""),
            10
          )
        : null,

    recommendation: recommended
      ? {
          id: recommended.id,
          name: recommended.name,
          reason: recommended.reason ?? response.decisionSummary,
        }
      : null,

    recommendedCandidate: recommended
      ? {
          id: recommended.id,
          name: recommended.name,
          status: recommended.status,
          safety: recommended.safety,
          opportunity: recommended.opportunity,
          uncertainty: recommended.uncertainty,
          distance: recommended.distance,
          confidence:
            recommended.confidence != null
              ? Number.parseInt(
                  String(recommended.confidence).replace("%", ""),
                  10
                )
              : null,
          lat: recommended.lat,
          lng: recommended.lng,
          reason: recommended.reason,
        }
      : null,

    candidates: candidates.map((candidate) => ({
      id: candidate.id,
      name: candidate.name,
      status: candidate.status,
      safety: candidate.safety,
      opportunity: candidate.opportunity,
      uncertainty: candidate.uncertainty,
      distance: candidate.distance,
      confidence:
        candidate.confidence != null
          ? Number.parseInt(
              String(candidate.confidence).replace("%", ""),
              10
            )
          : null,
      lat: candidate.lat,
      lng: candidate.lng,
      reason: candidate.reason,
      opportunityStatus: null,
    })),

    marineSafety: {
      status:
        recommended?.safety === 1
          ? "SAFE"
          : recommended?.safety === 0
            ? "UNSAFE"
            : "UNKNOWN",
      reasons: [],
    },

    marineConditions: null,

    uncertainty: recommended
      ? {
          level:
            recommended.uncertainty != null
              ? `${recommended.uncertainty}%`
              : "UNKNOWN",
          score: recommended.uncertainty ?? 0,
          explanation:
            "Uncertainty supplied by the M4 decision response.",
        }
      : null,

    evidence: response.evidence ?? [],

    tradeoffs: response.tradeoffs ?? [],

    decisionSummary:
      response.decisionSummary ??
      "No decision summary available.",

    rejectedCandidates: rejected,

    dataMode: response.dataMode ?? "DEMO",
  };
}