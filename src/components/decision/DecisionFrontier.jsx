function getConfidence(candidate) {
  if (
    candidate?.confidence === null ||
    candidate?.confidence === undefined
  ) {
    return null;
  }

  const value =
    Number(candidate.confidence);

  return Number.isFinite(value)
    ? value
    : null;
}


function getDistance(candidate) {
  if (
    candidate?.distance === null ||
    candidate?.distance === undefined
  ) {
    return null;
  }

  const value =
    Number(candidate.distance);

  return Number.isFinite(value)
    ? value
    : null;
}


function getStateLabel(status) {
  switch (status) {
    case "RECOMMENDED":
      return "RECOMMENDED";

    case "ALTERNATIVE":
      return "ALTERNATIVE";

    case "UNSAFE":
      return "UNSAFE";

    case "INSUFFICIENT_EVIDENCE":
      return "INSUFFICIENT EVIDENCE";

    case "DOMINATED":
      return "DOMINATED";

    case "REJECTED":
      return "REJECTED";

    default:
      return status ?? "UNKNOWN";
  }
}


function getPointColor(status) {
  switch (status) {
    case "RECOMMENDED":
      return "#55d69b";

    case "ALTERNATIVE":
      return "#e4bd57";

    case "UNSAFE":
      return "#e56b6f";

    case "INSUFFICIENT_EVIDENCE":
      return "#9a7fd1";

    case "DOMINATED":
      return "#8b6f5a";

    case "REJECTED":
      return "#e56b6f";

    default:
      return "#718797";
  }
}


function getParetoId(point) {
  if (!point) {
    return null;
  }

  return (
    point.id ??
    point.candidate_id ??
    point.candidateId ??
    point.pfz_id ??
    null
  );
}


function getParetoX(point) {
  if (!point) {
    return null;
  }

  const value =
    Number(
      point.distance ??
      point.distance_km ??
      point.x
    );

  return Number.isFinite(value)
    ? value
    : null;
}


function getParetoY(point) {
  if (!point) {
    return null;
  }

  const value =
    Number(
      point.confidence ??
      point.y
    );

  return Number.isFinite(value)
    ? value
    : null;
}


function normalizeParetoPoints(
  points
) {
  if (
    !Array.isArray(points)
  ) {
    return [];
  }

  return points
    .map(
      (point) => ({
        id:
          getParetoId(point),

        x:
          getParetoX(point),

        y:
          getParetoY(point),

        status:
          point.status ??
          null,

        name:
          point.name ??
          point.candidate_name ??
          point.candidateName ??
          getParetoId(point) ??
          "Pareto point",
      })
    )
    .filter(
      (point) =>
        point.id !== null &&
        point.x !== null &&
        point.y !== null
    );
}


function DecisionFrontier({
  candidates = [],
  paretoPoints = [],
  selectedCandidateId = null,
  onCandidateSelect,
}) {
  const authoritativeParetoPoints =
    normalizeParetoPoints(
      paretoPoints
    );


  const validCandidates =
    candidates.filter(
      (candidate) =>
        getConfidence(candidate) !== null &&
        getDistance(candidate) !== null
    );


  const usingAuthoritativePareto =
    authoritativeParetoPoints.length > 0;


  const points =
    usingAuthoritativePareto
      ? authoritativeParetoPoints
      : validCandidates.map(
        (candidate) => ({
          id:
            candidate.id,

          x:
            getDistance(candidate),

          y:
            getConfidence(candidate),

          status:
            candidate.status,

          name:
            candidate.name,
        })
      );


  const maxDistance =
    points.length > 0
      ? Math.max(
        ...points.map(
          (point) => point.x
        )
      )
      : 1;


  const minDistance =
    points.length > 0
      ? Math.min(
        ...points.map(
          (point) => point.x
        )
      )
      : 0;


  const distanceRange =
    Math.max(
      maxDistance - minDistance,
      1
    );


  return (
    <section className="decision-frontier">

      <div className="panel-title">

        <span>
          DECISION FRONTIER
        </span>

        <span>
          {usingAuthoritativePareto
            ? "PARETO DATA"
            : "TRADE-OFF VIEW"}
        </span>

      </div>


      <div className="frontier-intro">

        <h2>
          {usingAuthoritativePareto
            ? "Authoritative Pareto frontier"
            : "Candidate trade-offs"}
        </h2>

        <p>
          {usingAuthoritativePareto
            ? (
              "This frontier displays Pareto information supplied by the authoritative decision service. M3 does not calculate dominance or optimization."
            )
            : (
              "This view compares backend-supplied candidate attributes. A Pareto frontier is not calculated because authoritative Pareto data was not supplied."
            )}
        </p>

      </div>


      {points.length > 0 ? (

        <>

          <div
            style={{
              position: "relative",
              height: "320px",
              marginTop: "24px",
              marginBottom: "20px",
              borderLeft:
                "1px solid #345064",
              borderBottom:
                "1px solid #345064",
              background:
                "linear-gradient(to top, rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(to right, rgba(255,255,255,0.025) 1px, transparent 1px)",
              backgroundSize:
                "20% 20%",
            }}
          >

            <span
              style={{
                position: "absolute",
                left: "-32px",
                top: "4px",
                fontSize: "10px",
                color: "#718797",
                writingMode:
                  "vertical-rl",
                transform:
                  "rotate(180deg)",
              }}
            >
              CONFIDENCE
            </span>


            <span
              style={{
                position: "absolute",
                right: "4px",
                bottom: "-24px",
                fontSize: "10px",
                color: "#718797",
              }}
            >
              DISTANCE →
            </span>


            {points.map(
              (point) => {

                const x =
                  8 +
                  (
                    (
                      point.x -
                      minDistance
                    ) /
                    distanceRange
                  ) *
                  84;


                const y =
                  8 +
                  (
                    100 -
                    point.y
                  ) *
                  0.84;


                const selected =
                  selectedCandidateId ===
                  point.id;


                const pointColor =
                  getPointColor(
                    point.status
                  );


                return (
                  <button
                    key={
                      point.id
                    }

                    type="button"

                    onClick={() => {

                      if (
                        onCandidateSelect
                      ) {

                        const candidate =
                          candidates.find(
                            (item) =>
                              item.id ===
                              point.id
                          );

                        if (candidate) {
                          onCandidateSelect(
                            candidate
                          );
                        }

                      }

                    }}

                    aria-label={
                      `${point.name}, ` +
                      `${getStateLabel(
                        point.status
                      )}, ` +
                      `${point.y}% confidence, ` +
                      `${point.x} km distance`
                    }

                    style={{
                      position:
                        "absolute",

                      left:
                        `${x}%`,

                      top:
                        `${y}%`,

                      transform:
                        "translate(-50%, -50%)",

                      width:
                        selected
                          ? "20px"
                          : "15px",

                      height:
                        selected
                          ? "20px"
                          : "15px",

                      borderRadius:
                        "50%",

                      border:
                        selected
                          ? "3px solid #ffffff"
                          : `2px solid ${pointColor}`,

                      background:
                        pointColor,

                      cursor:
                        "pointer",

                      boxShadow:
                        selected
                          ? `0 0 0 5px ${pointColor}33`
                          : "none",
                    }}
                  />
                );

              }
            )}

          </div>


          <div
            style={{
              display:
                "flex",

              flexWrap:
                "wrap",

              gap:
                "10px",
            }}
          >

            {points.map(
              (point) => (

                <button
                  key={
                    `legend-${point.id}`
                  }

                  type="button"

                  onClick={() => {

                    if (
                      onCandidateSelect
                    ) {

                      const candidate =
                        candidates.find(
                          (item) =>
                            item.id ===
                            point.id
                        );

                      if (candidate) {
                        onCandidateSelect(
                          candidate
                        );
                      }

                    }

                  }}

                  style={{
                    display:
                      "flex",

                    alignItems:
                      "center",

                    gap:
                      "7px",

                    padding:
                      "8px 10px",

                    borderRadius:
                      "7px",

                    border:
                      selectedCandidateId ===
                      point.id
                        ? "1px solid #ffffff"
                        : "1px solid #223b4d",

                    background:
                      "#0f1e2b",

                    color:
                      "#d8e4ec",

                    cursor:
                      "pointer",
                  }}
                >

                  <span
                    style={{
                      width:
                        "9px",

                      height:
                        "9px",

                      borderRadius:
                        "50%",

                      background:
                        getPointColor(
                          point.status
                        ),
                    }}
                  />

                  <span>
                    {point.name}
                  </span>

                  <small>
                    {getStateLabel(
                      point.status
                    )}
                  </small>

                </button>

              )
            )}

          </div>

        </>

      ) : (

        <div
          className="integration-status"
        >

          <strong>
            FRONTIER UNAVAILABLE
          </strong>

          <span>
            Authoritative Pareto data was not
            supplied, and candidate confidence
            and distance attributes are not
            sufficient to construct a trade-off
            view.
          </span>

        </div>

      )}


      <div
        style={{
          marginTop:
            "20px",

          padding:
            "15px",

          border:
            "1px solid #223b4d",

          borderRadius:
            "8px",

          background:
            "#0b1722",
        }}
      >

        <strong
          style={{
            display:
              "block",

            fontSize:
              "11px",

            letterSpacing:
              "0.08em",

            marginBottom:
              "6px",
          }}
        >
          INTERPRETATION
        </strong>

        <span
          style={{
            color:
              "#aab8c3",

            fontSize:
              "13px",

            lineHeight:
              "1.5",
          }}
        >
          {usingAuthoritativePareto
            ? (
              "Pareto information comes from the authoritative decision service. M3 only renders the supplied result."
            )
            : (
              "The trade-off view visualizes supplied candidate attributes. It does not perform ranking, dominance analysis, safety assessment, Pareto calculation, or optimization."
            )}
        </span>

      </div>

    </section>
  );
}


export default DecisionFrontier;