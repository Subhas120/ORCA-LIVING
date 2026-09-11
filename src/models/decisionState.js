export const decisionState = {
  objective: {
    text: "Find the safest useful fishing opportunity tomorrow morning",
    vessel: "Small vessel",
    time: "Tomorrow morning"
  },

  recommendedCandidate: {
    id: "A",
    name: "Candidate A",
    status: "RECOMMENDED",
    safety: 92,
    opportunity: 87,
    uncertainty: 18,
    distance: 12,
    confidence: "HIGH"
  },

  alternativeCandidates: [
    {
      id: "C",
      name: "Candidate C",
      status: "ALTERNATIVE",
      safety: 84,
      opportunity: 91,
      uncertainty: 31,
      distance: 24,
      confidence: "MEDIUM"
    }
  ],

  rejectedCandidates: [
    {
      id: "B",
      name: "Candidate B",
      status: "REJECTED",
      reason: "High wave exposure",
      safety: 38,
      opportunity: 90,
      uncertainty: 22,
      distance: 18
    }
  ],

  decisionSummary:
    "Candidate A provides the best balance of safety, opportunity, distance and uncertainty.",

  tradeoffs: [
    "Strong safety margin",
    "High opportunity indicators",
    "Shorter travel distance",
    "Low uncertainty"
  ],

  uncertainty: {
    level: "HIGH",
    score: 18,
    explanation: "Evidence is consistent and recent."
  },

  evidence: [
    {
      id: "E1",
      category: "Safety",
      observation: "Wave height = 1.6 m",
      source: "Ocean forecast",
      timestamp: "2026-09-11 06:00"
    },
    {
      id: "E2",
      category: "Opportunity",
      observation: "Favorable chlorophyll conditions",
      source: "Satellite observation",
      timestamp: "2026-09-11 05:30"
    }
  ],

  sensitivity: {
    variable: "Wind",
    current: "15 kt",
    threshold: "22 kt",
    explanation:
      "If wind increases significantly, Candidate A may fall below the safety threshold."
  },

  dataMode: "SIMULATED"
};