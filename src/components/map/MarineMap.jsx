import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

import { useEffect } from "react";

import "leaflet/dist/leaflet.css";


function FitCandidates({ candidates }) {
  const map = useMap();

  useEffect(() => {
    const validCandidates =
      candidates.filter(
        (candidate) =>
          typeof candidate.lat === "number" &&
          typeof candidate.lng === "number"
      );

    if (validCandidates.length === 0) {
      return;
    }

    if (validCandidates.length === 1) {
      map.setView(
        [
          validCandidates[0].lat,
          validCandidates[0].lng,
        ],
        9
      );

      return;
    }

    const bounds = validCandidates.map(
      (candidate) => [
        candidate.lat,
        candidate.lng,
      ]
    );

    map.fitBounds(bounds, {
      padding: [50, 50],
      maxZoom: 9,
    });
  }, [candidates, map]);

  return null;
}


function MarineMap({ candidates = [] }) {
  return (
    <MapContainer
      center={[9.8, 76.14]}
      zoom={9}
      style={{
        height: "500px",
        width: "100%",
      }}
    >

      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <FitCandidates
        candidates={candidates}
      />

      {candidates.map((candidate) => {

        let color = "#55d69b";

        if (
          candidate.status ===
          "REJECTED"
        ) {
          color = "#e56b6f";
        }

        if (
          candidate.status ===
          "ALTERNATIVE"
        ) {
          color = "#e4bd57";
        }

        return (
          <CircleMarker
            key={candidate.id}
            center={[
              candidate.lat,
              candidate.lng,
            ]}
            radius={10}
            pathOptions={{
              color,
              fillColor: color,
              fillOpacity: 0.85,
            }}
          >

            <Popup>

              <strong>
                {candidate.name}
              </strong>

              <br />

              Status:{" "}
              {candidate.status}

              <br />

              Opportunity:{" "}
              {candidate.opportunityStatus ??
                candidate.opportunity ??
                "—"}

              <br />

              Distance:{" "}
              {candidate.distance ??
                "—"} km

              <br />

              Confidence:{" "}
              {candidate.confidence ??
                "—"}%

            </Popup>

          </CircleMarker>
        );
      })}

    </MapContainer>
  );
}

export default MarineMap;