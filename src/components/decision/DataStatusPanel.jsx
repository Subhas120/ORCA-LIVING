function formatTimestamp(
  timestamp
) {
  if (!timestamp) {
    return "Timestamp unavailable";
  }

  const date =
    new Date(timestamp);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return timestamp;
  }

  return date.toLocaleString();
}


function getFreshness(
  timestamp
) {
  if (!timestamp) {
    return {
      label: "UNKNOWN",
      detail: "No observation timestamp was supplied.",
    };
  }

  const date =
    new Date(timestamp);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return {
      label: "UNKNOWN",
      detail: "The supplied timestamp could not be interpreted.",
    };
  }

  const age =
    Date.now() -
    date.getTime();

  if (age < 0) {
    return {
      label: "CURRENT",
      detail: "The supplied observation timestamp is current.",
    };
  }

  const ageHours =
    age /
    (1000 * 60 * 60);

  if (ageHours <= 6) {
    return {
      label: "RECENT",
      detail: "The observation is within the last 6 hours.",
    };
  }

  if (ageHours <= 24) {
    return {
      label: "OLDER",
      detail: "The observation is more than 6 hours old.",
    };
  }

  return {
    label: "STALE",
    detail: "The observation is more than 24 hours old.",
  };
}


function DataStatusPanel({
  dataMode = "UNKNOWN",
  status = null,
  source = null,
  timestamp = null,
  confidence = null,
  evidence = [],
}) {
  const freshness =
    getFreshness(
      timestamp
    );


  const isSimulated =
    dataMode ===
    "SIMULATED";


  const hasEvidence =
    Array.isArray(evidence) &&
    evidence.length > 0;


  const informationGaps =
    evidence.filter(
      (item) =>
        !item.source ||
        !item.timestamp
    ).length;


  return (
    <section
      className="data-status-panel"
      aria-labelledby="data-status-title"
    >

      <div className="panel-title">

        <span id="data-status-title">
          DATA STATUS
        </span>

        <span>
          {isSimulated
            ? "DEMO DATA"
            : "BACKEND DATA"}
        </span>

      </div>


      <div className="data-status-grid">


        <div className="data-status-item">

          <span>
            SOURCE
          </span>

          <strong>
            {source ??
              "SOURCE UNAVAILABLE"}
          </strong>

        </div>


        <div className="data-status-item">

          <span>
            LAST UPDATED
          </span>

          <strong>
            {formatTimestamp(
              timestamp
            )}
          </strong>

        </div>


        <div className="data-status-item">

          <span>
            FRESHNESS
          </span>

          <strong>
            {freshness.label}
          </strong>

        </div>


        <div className="data-status-item">

          <span>
            DECISION STATUS
          </span>

          <strong>
            {status ??
              "UNKNOWN"}
          </strong>

        </div>


        <div className="data-status-item">

          <span>
            CONFIDENCE
          </span>

          <strong>
            {confidence !== null &&
            confidence !== undefined
              ? `${confidence}%`
              : "UNKNOWN"}
          </strong>

        </div>


        <div className="data-status-item">

          <span>
            EVIDENCE RECORDS
          </span>

          <strong>
            {hasEvidence
              ? evidence.length
              : "NONE"}
          </strong>

        </div>

      </div>


      <div className="data-status-message">

        <strong>
          {isSimulated
            ? "SIMULATED DATA"
            : "DATA LINEAGE"}
        </strong>

        <p>
          {isSimulated
            ? "This information is demonstration data and must not be interpreted as live marine observations."
            : source
              ? `Decision data was supplied by ${source}. M3 displays the supplied provenance without creating new scientific values.`
              : "The backend did not supply a source identifier."}
        </p>

      </div>


      <div className="data-status-freshness">

        <strong>
          FRESHNESS
        </strong>

        <span>
          {freshness.detail}
        </span>

      </div>


      {informationGaps > 0 && (

        <div
          className="data-status-warning"
          role="status"
        >

          <strong>
            INFORMATION GAP
          </strong>

          <span>
            {informationGaps} evidence{" "}
            {informationGaps === 1
              ? "record"
              : "records"}{" "}
            {informationGaps === 1
              ? "is"
              : "are"}{" "}
            missing source or timestamp
            information.
          </span>

        </div>

      )}

    </section>
  );
}


export default DataStatusPanel;