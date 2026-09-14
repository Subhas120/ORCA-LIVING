function formatConfidence(confidence) {
  if (confidence === null || confidence === undefined) {
    return "—";
  }

  if (typeof confidence === "number") {
    return `${confidence}%`;
  }

  return confidence;
}

function EvidencePanel({
  candidate,
  evidence = [],
  dataMode = "SIMULATED",
}) {
  return (
    <section className="evidence-panel">

      <div className="panel-title">
        <span>EVIDENCE</span>
        <span>DECISION SUPPORT</span>
      </div>


      <div className="evidence-summary">

        <div>
          <h2>
            Why this location?
          </h2>

          <p>
            The recommendation is supported by
            environmental observations and their
            associated provenance.
          </p>
        </div>

      </div>


      <div className="evidence-list">

        {evidence.length > 0 ? (

          evidence.map((item, index) => (

            <div
              className="evidence-item"
              key={
                item.id ??
                item.parameter ??
                `evidence-${index}`
              }
            >

              <div className="evidence-main">

                <div className="evidence-category">
                  {item.parameter ??
                    item.category ??
                    "Marine observation"}
                </div>


                <strong>
                  {item.observation ??
                    item.value ??
                    item.parameter ??
                    "Observation available"}
                </strong>


                <span>
                  Source:{" "}
                  {item.source ??
                    "Unknown source"}
                </span>


                <span>
                  Observed:{" "}
                  {item.timestamp ??
                    "Timestamp unavailable"}
                </span>


                {item.confidence !== null &&
                  item.confidence !== undefined && (

                    <span>
                      Evidence confidence:{" "}
                      {formatConfidence(item.confidence)}
                    </span>

                  )}

              </div>


              <div className="evidence-id">
                {item.id ??
                  item.parameter ??
                  `E${index + 1}`}
              </div>

            </div>

          ))

        ) : (

          <div className="evidence-item">

            <div className="evidence-main">

              <div className="evidence-category">
                EVIDENCE UNAVAILABLE
              </div>

              <strong>
                No evidence records are currently
                available.
              </strong>

              <span>
                The backend has not supplied evidence
                for this decision.
              </span>

            </div>

          </div>

        )}

      </div>


      <div className="evidence-signals">

        <div>
          <span>DISTANCE</span>

          <strong>
            {candidate?.distance !== null &&
            candidate?.distance !== undefined
              ? `${candidate.distance} km`
              : "—"}
          </strong>
        </div>


        <div>
          <span>OPPORTUNITY</span>

          <strong>
            {candidate?.opportunityStatus ??
              (candidate?.opportunity !== null &&
              candidate?.opportunity !== undefined
                ? `${candidate.opportunity}%`
                : "—")}
          </strong>
        </div>


        <div>
          <span>CONFIDENCE</span>

          <strong>
            {formatConfidence(
              candidate?.confidence
            )}
          </strong>
        </div>


        <div>
          <span>LOCATION</span>

          <strong>
            {candidate?.lat !== undefined &&
            candidate?.lng !== undefined
              ? `${candidate.lat.toFixed(2)}°, ${candidate.lng.toFixed(2)}°`
              : "—"}
          </strong>
        </div>

      </div>


      <div className="evidence-footer">

        <div>
          <span>DATA MODE</span>

          <strong>
            {dataMode}
          </strong>
        </div>


        <div>
          <span>PROVENANCE</span>

          <strong>
            SOURCE + TIMESTAMP
          </strong>
        </div>

      </div>

    </section>
  );
}

export default EvidencePanel;