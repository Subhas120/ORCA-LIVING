/*
 * ORCA M3 GIS ADAPTER
 *
 * Converts optional backend GIS information into a
 * frontend-friendly structure.
 *
 * IMPORTANT:
 * M3 does not create route geometry, geofences,
 * hazard polygons, marine boundaries, or safe areas.
 *
 * Geometry is displayed only when supplied by an
 * authoritative backend service.
 */


function isValidCoordinate(
  coordinate
) {
  return (
    Array.isArray(coordinate) &&
    coordinate.length >= 2 &&
    typeof coordinate[0] === "number" &&
    Number.isFinite(coordinate[0]) &&
    typeof coordinate[1] === "number" &&
    Number.isFinite(coordinate[1]) &&
    coordinate[0] >= -90 &&
    coordinate[0] <= 90 &&
    coordinate[1] >= -180 &&
    coordinate[1] <= 180
  );
}


function normalizeGeometry(
  geometry
) {
  if (
    !geometry ||
    typeof geometry !== "object"
  ) {
    return null;
  }

  if (
    typeof geometry.type !== "string"
  ) {
    return null;
  }

  if (
    geometry.coordinates === undefined
  ) {
    return null;
  }

  return geometry;
}


function normalizeFeature(
  feature,
  index
) {
  if (
    !feature ||
    typeof feature !== "object"
  ) {
    return null;
  }

  const geometry =
    normalizeGeometry(
      feature.geometry
    );

  if (!geometry) {
    return null;
  }

  return {
    id:
      feature.id ??
      `feature-${index}`,

    type:
      feature.type ??
      "Feature",

    properties:
      feature.properties ??
      {},

    geometry,
  };
}


function normalizeFeatureCollection(
  value
) {
  if (
    !value ||
    typeof value !== "object"
  ) {
    return [];
  }

  if (
    value.type ===
    "FeatureCollection" &&
    Array.isArray(value.features)
  ) {
    return value.features
      .map(
        normalizeFeature
      )
      .filter(
        Boolean
      );
  }

  if (
    value.type === "Feature"
  ) {
    const feature =
      normalizeFeature(
        value,
        0
      );

    return feature
      ? [feature]
      : [];
  }

  return [];
}


function normalizeRoute(
  route
) {
  if (
    !route ||
    typeof route !== "object"
  ) {
    return null;
  }

  const geometry =
    normalizeGeometry(
      route.geometry
    );

  const coordinates =
    Array.isArray(
      route.coordinates
    )
      ? route.coordinates.filter(
          isValidCoordinate
        )
      : [];

  if (
    !geometry &&
    coordinates.length === 0
  ) {
    return null;
  }

  return {
    id:
      route.id ??
      null,

    origin:
      route.origin ??
      null,

    destination:
      route.destination ??
      null,

    distanceKm:
      route.distance_km ??
      route.distanceKm ??
      null,

    algorithm:
      route.algorithm ??
      null,

    blockedCells:
      Array.isArray(
        route.blocked_cells
      )
        ? route.blocked_cells
        : [],

    restrictedZonePolicy:
      route.restricted_zone_policy ??
      null,

    costModel:
      route.cost_model ??
      null,

    geometry,

    coordinates,
  };
}


export function adaptGISData(
  source
) {
  if (
    !source ||
    typeof source !== "object"
  ) {
    return {
      routes: [],
      geofences: [],
      hazards: [],
      marineRegions: [],
      safeAreas: [],
      unsafeAreas: [],
      available: false,
    };
  }


  const routesSource =
    source.routes ??
    source.route ??
    null;


  const routes =
    Array.isArray(routesSource)
      ? routesSource
          .map(
            normalizeRoute
          )
          .filter(
            Boolean
          )
      : (
        normalizeRoute(
          routesSource
        )
          ? [
            normalizeRoute(
              routesSource
            ),
          ]
          : []
      );


  const geofences =
    normalizeFeatureCollection(
      source.geofences ??
      source.geofence
    );


  const hazards =
    normalizeFeatureCollection(
      source.hazard_geometry ??
      source.hazardGeometry ??
      source.hazards
    );


  const marineRegions =
    normalizeFeatureCollection(
      source.marine_regions ??
      source.marineRegions
    );


  const safeAreas =
    normalizeFeatureCollection(
      source.safe_areas ??
      source.safeAreas
    );


  const unsafeAreas =
    normalizeFeatureCollection(
      source.unsafe_areas ??
      source.unsafeAreas
    );


  const available =
    routes.length > 0 ||
    geofences.length > 0 ||
    hazards.length > 0 ||
    marineRegions.length > 0 ||
    safeAreas.length > 0 ||
    unsafeAreas.length > 0;


  return {
    routes,
    geofences,
    hazards,
    marineRegions,
    safeAreas,
    unsafeAreas,
    available,
  };
}