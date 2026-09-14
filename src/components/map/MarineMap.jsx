import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

function MarineMap({ candidates }) {
  return (
    <MapContainer
      center={[12.92, 74.85]}
      zoom={9}
      style={{ height: "500px", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {candidates.map((candidate) => {
        let color = "#55d69b";

        if (candidate.status === "REJECTED") {
          color = "#e56b6f";
        }

        if (candidate.status === "ALTERNATIVE") {
          color = "#e4bd57";
        }

        return (
          <CircleMarker
            key={candidate.id}
            center={[candidate.lat, candidate.lng]}
            radius={10}
            pathOptions={{
              color,
              fillColor: color,
              fillOpacity: 0.8,
            }}
          >
            <Popup>
              <strong>{candidate.name}</strong>
              <br />
              Status: {candidate.status}
              <br />
              Safety: {candidate.safety}%
              <br />
              Opportunity: {candidate.opportunity}%
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}

export default MarineMap;