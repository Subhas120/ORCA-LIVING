function getConfidence(candidate) {
  if (
    candidate?.confidence === null ||
    candidate?.confidence === undefined
  ) {
    return null;
  }

  return Number(candidate.confidence);
}


function getDistance(candidate) {
  if (
    candidate?.distance === null ||
    candidate?.distance === undefined
  ) {
    return null;
  }

  return Number(candidate.distance);
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


function DecisionFrontier({
  candidates = [],
  selectedCandidateId = null,
  onCandidateSelect,
}) {
  const validCandidates = candidates.filter(
    (candidate) =>
      getConfidence(candidate) !== null &&
      getDistance(candidate) !== null
  );


  const maxDistance =
    validCandidates.length > 0
      ? Math.max(
        ...validCandidates.map(
          (candidate) =>
            getDistance(candidate)
        )
      )
      : 1;


  const minDistance =
    validCandidates.length > 0
      ? Math.min(
        ...validCandidates.map(
          (candidate) =>
            getDistance(candidate)
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
          TRADE-OFF VIEW
        </span>

      </div>


      <div className="frontier-intro">

        <h2>
          Candidate trade-offs
        </h2>

        <p>
          This view compares backend-supplied
          candidate attributes. It does not
          calculate a new recommendation.
        </p>

      </div>


      {validCandidates.length > 0 ? (

        <>

          <div
            style={{
              position: "relative",
              height: "320px",
              marginTop: "24px",
              marginBottom: "20px",
              borderLeft: "1px solid #345064",
              borderBottom: "1px solid #345064",
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
                writingMode: "vertical-rl",
                transform: "rotate(180deg)",
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


            {validCandidates.map(
              (candidate) => {

                const confidence =
                  getConfidence(candidate);

                const distance =
                  getDistance(candidate);

                const x =
                  8 +
                  (
                    (
                      distance -
                      minDistance
                    ) /
                    distanceRange
                  ) *
                  84;

                const y =
                  8 +
                  (
                    100 -
                    confidence
                  ) *
                  0.84;

                const selected =
                  selectedCandidateId ===
                  candidate.id;

                const pointColor =
                  getPointColor(
                    candidate.status
                  );


                return (
                  <button
                    key={candidate.id}
                    type="button"
                    onClick={() => {
                      if (
                        onCandidateSelect
                      ) {
                        onCandidateSelect(
                          candidate
                        );
                      }
                    }}
                    aria-label={
                      `${candidate.name}, ` +
                      `${getStateLabel(candidate.status)}, ` +
                      `${confidence}% confidence, ` +
                      `${distance} km distance`
                    }
                    style={{
                      position: "absolute",
                      left: `${x}%`,
                      top: `${y}%`,
                      transform:
                        "translate(-50%, -50%)",
                      width: selected
                        ? "20px"
                        : "15px",
                      height: selected
                        ? "20px"
                        : "15px",
                      borderRadius: "50%",
                      border: selected
                        ? "3px solid #ffffff"
                        : `2px solid ${pointColor}`,
                      background: pointColor,
                      cursor: "pointer",
                      boxShadow: selected
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
              display: "flex",
              flexWrap: "wrap",
              gap: "10px",
            }}
          >

            {validCandidates.map(
              (candidate) => (

                <button
                  key={candidate.id}
                  type="button"
                  onClick={() => {
                    if (
                      onCandidateSelect
                    ) {
                      onCandidateSelect(
                        candidate
                      );
                    }
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "7px",
                    padding: "8px 10px",
                    borderRadius: "7px",
                    border:
                      selectedCandidateId ===
                      candidate.id
                        ? "1px solid #ffffff"
                        : "1px solid #223b4d",
                    background: "#0f1e2b",
                    color: "#d8e4ec",
                    cursor: "pointer",
                  }}
                >

                  <span
                    style={{
                      width: "9px",
                      height: "9px",
                      borderRadius: "50%",
                      background:
                        getPointColor(
                          candidate.status
                        ),
                    }}
                  />

                  <span>
                    {candidate.name}
                  </span>

                  <small>
                    {getStateLabel(
                      candidate.status
                    )}
                  </small>

                </button>

              )
            )}

          </div>

        </>

      ) : (

        <div className="integration-status">

          <strong>
            FRONTIER UNAVAILABLE
          </strong>

          <span>
            Candidate confidence and distance
            attributes are required from the
            authoritative decision service.
          </span>

        </div>

      )}


      <div
        style={{
          marginTop: "20px",
          padding: "15px",
          border: "1px solid #223b4d",
          borderRadius: "8px",
          background: "#0b1722",
        }}
      >

        <strong
          style={{
            display: "block",
            fontSize: "11px",
            letterSpacing: "0.08em",
            marginBottom: "6px",
          }}
        >
          INTERPRETATION
        </strong>

        <span
          style={{
            color: "#aab8c3",
            fontSize: "13px",
            lineHeight: "1.5",
          }}
        >
          The frontier visualizes attributes supplied
          by the decision service. It does not perform
          ranking, dominance analysis, safety assessment,
          or optimization in the frontend.
        </span>

      </div>

    </section>
  );
}


export default DecisionFrontier;