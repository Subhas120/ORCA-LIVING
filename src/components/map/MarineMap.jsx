import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  CircleMarker,
  GeoJSON,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";


const DEFAULT_CENTER = [
  12.92,
  74.85,
];


const DEFAULT_ZOOM = 7;


function isValidCoordinate(
  latitude,
  longitude
) {
  return (
    typeof latitude === "number" &&
    Number.isFinite(latitude) &&
    latitude >= -90 &&
    latitude <= 90 &&
    typeof longitude === "number" &&
    Number.isFinite(longitude) &&
    longitude >= -180 &&
    longitude <= 180
  );
}


function FitCandidates({
  candidates,
}) {
  const map =
    useMap();


  useEffect(() => {
    const validCandidates =
      candidates.filter(
        (candidate) =>
          isValidCoordinate(
            candidate.lat,
            candidate.lng
          )
      );


    if (
      validCandidates.length === 0
    ) {
      return;
    }


    if (
      validCandidates.length === 1
    ) {
      map.setView(
        [
          validCandidates[0].lat,
          validCandidates[0].lng,
        ],
        9
      );

      return;
    }


    const bounds =
      validCandidates.map(
        (candidate) => [
          candidate.lat,
          candidate.lng,
        ]
      );


    map.fitBounds(
      bounds,
      {
        padding: [
          30,
          30,
        ],
      }
    );

  }, [
    candidates,
    map,
  ]);


  return null;
}


function MapContent({
  candidates,
  selectedCandidateId,
  onCandidateSelect,
  gis,
}) {
  const [tileError, setTileError] =
    useState(false);


  const validCandidates =
    useMemo(
      () =>
        candidates.filter(
          (candidate) =>
            isValidCoordinate(
              candidate.lat,
              candidate.lng
            )
        ),
      [candidates]
    );


  const invalidCandidateCount =
    candidates.length -
    validCandidates.length;


  useEffect(() => {
    const handleTileError =
      () => {
        setTileError(true);
      };


    window.addEventListener(
      "orca-map-tile-error",
      handleTileError
    );


    return () => {
      window.removeEventListener(
        "orca-map-tile-error",
        handleTileError
      );
    };
  }, []);


  const routeFeatures =
    Array.isArray(gis?.routes)
      ? gis.routes
      : [];


  const geofences =
    Array.isArray(gis?.geofences)
      ? gis.geofences
      : [];


  const hazardFeatures =
    Array.isArray(gis?.hazards)
      ? gis.hazards
      : [];


  const marineRegions =
    Array.isArray(gis?.marineRegions)
      ? gis.marineRegions
      : [];


  const safeAreas =
    Array.isArray(gis?.safeAreas)
      ? gis.safeAreas
      : [];


  const unsafeAreas =
    Array.isArray(gis?.unsafeAreas)
      ? gis.unsafeAreas
      : [];


  const hasGIS =
    Boolean(gis?.available);


  return (
    <>

      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
        eventHandlers={{
          tileerror: () => {
            setTileError(true);

            window.dispatchEvent(
              new Event(
                "orca-map-tile-error"
              )
            );
          },
        }}
      />


      <FitCandidates
        candidates={
          validCandidates
        }
      />


      {marineRegions.map(
        (feature) => (

          <GeoJSON
            key={
              `region-${feature.id}`
            }
            data={
              feature
            }
            pathOptions={{
              weight: 1,
              fillOpacity: 0.05,
            }}
          />

        )
      )}


      {safeAreas.map(
        (feature) => (

          <GeoJSON
            key={
              `safe-${feature.id}`
            }
            data={
              feature
            }
            pathOptions={{
              weight: 2,
              fillOpacity: 0.08,
            }}
          />

        )
      )}


      {unsafeAreas.map(
        (feature) => (

          <GeoJSON
            key={
              `unsafe-${feature.id}`
            }
            data={
              feature
            }
            pathOptions={{
              weight: 2,
              fillOpacity: 0.12,
            }}
          />

        )
      )}


      {hazardFeatures.map(
        (feature) => (

          <GeoJSON
            key={
              `hazard-${feature.id}`
            }
            data={
              feature
            }
            pathOptions={{
              weight: 2,
              fillOpacity: 0.15,
            }}
          />

        )
      )}


      {geofences.map(
        (feature) => (

          <GeoJSON
            key={
              `geofence-${feature.id}`
            }
            data={
              feature
            }
            pathOptions={{
              weight: 2,
              fillOpacity: 0.1,
            }}
          />

        )
      )}


      {routeFeatures.map(
        (route) => {

          if (
            route.geometry
          ) {
            return (
              <GeoJSON
                key={
                  `route-${route.id ?? "route"}`
                }
                data={{
                  type: "Feature",
                  geometry:
                    route.geometry,
                  properties: {},
                }}
                pathOptions={{
                  weight: 4,
                }}
              />
            );
          }


          return null;
        }
      )}


      {validCandidates.map(
        (candidate) => {

          const selected =
            candidate.id ===
            selectedCandidateId;


          return (
            <CircleMarker
              key={
                candidate.id
              }
              center={[
                candidate.lat,
                candidate.lng,
              ]}
              radius={
                selected
                  ? 11
                  : 8
              }
              eventHandlers={{
                click: () =>
                  onCandidateSelect(
                    candidate
                  ),
              }}
            >

              <Popup>

                <strong>
                  {candidate.name}
                </strong>

                <br />

                Status:{" "}
                {candidate.status ??
                  "UNKNOWN"}

                <br />

                Distance:{" "}
                {candidate.distance ??
                  "—"} km

                <br />

                Confidence:{" "}
                {candidate.confidence !== null &&
                candidate.confidence !== undefined
                  ? `${candidate.confidence}%`
                  : "—"}

              </Popup>

            </CircleMarker>
          );
        }
      )}


      {invalidCandidateCount > 0 && (

        <div
          className="map-warning"
          role="status"
        >

          <strong>
            LOCATION DATA WARNING
          </strong>

          <span>
            {invalidCandidateCount} candidate{" "}
            {invalidCandidateCount === 1
              ? "has"
              : "have"}{" "}
            missing or invalid coordinates.
            No coordinates were fabricated.
          </span>

        </div>

      )}


      {!hasGIS && (

        <div
          className="map-gis-status"
          role="status"
        >

          <strong>
            GIS GEOMETRY NOT SUPPLIED
          </strong>

          <span>
            Routes, geofences, hazard geometry
            and marine boundaries will appear
            when supplied by the backend.
          </span>

        </div>

      )}


      {hasGIS && (

        <div
          className="map-gis-status"
          role="status"
        >

          <strong>
            BACKEND GIS ACTIVE
          </strong>

          <span>
            Displaying only GIS geometry supplied
            by the backend.
          </span>

        </div>

      )}


      {tileError && (

        <div
          className="map-warning"
          role="alert"
        >

          <strong>
            MAP SERVICE WARNING
          </strong>

          <span>
            The map tile service could not load
            some map imagery.
          </span>

        </div>

      )}

    </>
  );
}


function MarineMap({
  candidates = [],
  selectedCandidateId = null,
  onCandidateSelect = () => {},
  gis = null,
}) {
  const validCandidates =
    candidates.filter(
      (candidate) =>
        isValidCoordinate(
          candidate.lat,
          candidate.lng
        )
    );


  const mapCenter =
    validCandidates.length > 0
      ? [
        validCandidates[0].lat,
        validCandidates[0].lng,
      ]
      : DEFAULT_CENTER;


  if (
    candidates.length > 0 &&
    validCandidates.length === 0
  ) {
    return (
      <div className="map-fallback">

        <strong>
          MAP LOCATION UNAVAILABLE
        </strong>

        <span>
          Candidate records were supplied, but
          none contain valid coordinates.
          No location was fabricated.
        </span>

      </div>
    );
  }


  return (
    <div className="marine-map">

      <MapContainer
        center={
          mapCenter
        }
        zoom={
          DEFAULT_ZOOM
        }
        scrollWheelZoom
      >

        <MapContent
          candidates={
            candidates
          }

          selectedCandidateId={
            selectedCandidateId
          }

          onCandidateSelect={
            onCandidateSelect
          }

          gis={
            gis
          }

        />

      </MapContainer>

    </div>
  );
}


export default MarineMap;