export const candidates = [
  {
    id: "A",
    name: "Candidate A",
    status: "RECOMMENDED",
    lat: 12.95,
    lng: 74.75,
    safety: 92,
    opportunity: 87,
    uncertainty: 18,
    distance: 12,
    reason: "Best overall balance"
  },
  {
    id: "B",
    name: "Candidate B",
    status: "REJECTED",
    lat: 13.05,
    lng: 74.90,
    safety: 38,
    opportunity: 90,
    uncertainty: 22,
    distance: 18,
    reason: "High wave exposure"
  },
  {
    id: "C",
    name: "Candidate C",
    status: "ALTERNATIVE",
    lat: 12.82,
    lng: 74.95,
    safety: 84,
    opportunity: 91,
    uncertainty: 31,
    distance: 24,
    reason: "Higher opportunity but longer route"
  }
];

export const hazardZones = [
  {
    id: "H1",
    name: "High Wave Zone",
    type: "HAZARD"
  }
];

export const mapState = {
  center: [12.92, 74.85],
  zoom: 9,
  dataMode: "SIMULATED"
};