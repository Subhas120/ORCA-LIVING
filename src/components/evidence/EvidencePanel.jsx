function formatConfidence(confidence) {
  if (
    confidence === null ||
    confidence === undefined
  ) {
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
  const isBackendConnected =
    dataMode === "BACKEND CONNECTED";


  const hasSampleSource =
    evidence.some(
      (item) =>
        typeof item.source === "string" &&
        item.source
          .toLowerCase()
          .includes("sample")
    );


  return (
    <section className="evidence-panel">

      <div className="panel-title">

        <span>
          EVIDENCE
        </span>

        <span>
          DECISION SUPPORT
        </span>

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
                      {formatConfidence(
                        item.confidence
                      )}
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

          <span>
            DISTANCE
          </span>

          <strong>
            {candidate?.distance !== null &&
            candidate?.distance !== undefined
              ? `${candidate.distance} km`
              : "—"}
          </strong>

        </div>


        <div>

          <span>
            OPPORTUNITY
          </span>

          <strong>
            {candidate?.opportunityStatus ??
              (candidate?.opportunity !== null &&
              candidate?.opportunity !== undefined
                ? `${candidate.opportunity}%`
                : "—")}
          </strong>

        </div>


        <div>

          <span>
            CONFIDENCE
          </span>

          <strong>
            {formatConfidence(
              candidate?.confidence
            )}
          </strong>

        </div>


        <div>

          <span>
            LOCATION
          </span>

          <strong>
            {candidate?.lat !== undefined &&
            candidate?.lng !== undefined
              ? `${candidate.lat.toFixed(
                  2
                )}°, ${candidate.lng.toFixed(
                  2
                )}°`
              : "—"}
          </strong>

        </div>

      </div>


      <div className="evidence-footer">

        <div>

          <span>
            DATA MODE
          </span>

          <strong>
            {dataMode}
          </strong>

        </div>


        <div>

          <span>
            PROVENANCE
          </span>

          <strong>
            SOURCE + TIMESTAMP
          </strong>

        </div>

      </div>


      {isBackendConnected &&
        hasSampleSource && (

        <div
          style={{
            marginTop: "16px",
            padding: "14px 16px",
            border: "1px solid #685a2c",
            borderRadius: "8px",
            background: "#151914",
            display: "flex",
            flexDirection: "column",
            gap: "5px",
          }}
        >

          <strong
            style={{
              fontSize: "11px",
              letterSpacing: "0.08em",
            }}
          >
            PROTOTYPE DATA SOURCE
          </strong>

          <span
            style={{
              fontSize: "13px",
              lineHeight: "1.5",
              color: "#aab8c3",
            }}
          >
            The M2 backend is connected, but the
            supplied marine and PFZ observations are
            identified as sample/prototype data.
            They are not presented as live observations.
          </span>

        </div>

      )}

    </section>
  );
}


export default EvidencePanel;