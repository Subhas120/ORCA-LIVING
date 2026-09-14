function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "Timestamp unavailable";
  }

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString();
}

function getFreshness(timestamp) {
  if (!timestamp) {
    return {
      label: "UNKNOWN",
      detail: "No observation timestamp was supplied.",
    };
  }

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return {
      label: "UNKNOWN",
      detail: "The supplied timestamp could not be interpreted.",
    };
  }

  const age = Date.now() - date.getTime();

  if (age < 0) {
    return {
      label: "CURRENT",
      detail: "The supplied observation timestamp is current.",
    };
  }

  const ageHours = age / (1000 * 60 * 60);

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
  const freshness = getFreshness(timestamp);

  const normalizedDataMode =
    typeof dataMode === "string"
      ? dataMode.trim().toUpperCase()
      : "UNKNOWN";

  const isDemonstrationData =
    normalizedDataMode === "SIMULATED" ||
    normalizedDataMode === "DEMO" ||
    normalizedDataMode === "DEMONSTRATION";

  const hasEvidence =
    Array.isArray(evidence) &&
    evidence.length > 0;

  const informationGaps = Array.isArray(evidence)
    ? evidence.filter(
        (item) =>
          !item.source ||
          !item.timestamp
      ).length
    : 0;

  const cardStyle = {
    padding: "16px",
    border: "1px solid #223b4d",
    borderRadius: "8px",
    background: "#0f1e2b",
    minWidth: 0,
  };

  const labelStyle = {
    display: "block",
    marginBottom: "7px",
    fontSize: "10px",
    fontWeight: "600",
    letterSpacing: "0.09em",
    color: "#7691a4",
    textTransform: "uppercase",
  };

  const valueStyle = {
    display: "block",
    fontSize: "14px",
    lineHeight: "1.4",
    color: "#e5edf2",
    overflowWrap: "anywhere",
  };

  return (
    <section
      className="data-status-panel"
      aria-labelledby="data-status-title"
      style={{
        marginTop: "24px",
        overflow: "hidden",
      }}
    >
      <div
        className="panel-title"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
          padding: "16px 20px",
          borderBottom: "1px solid #223b4d",
        }}
      >
        <span id="data-status-title">
          DATA STATUS
        </span>

        <span
          style={{
            color: isDemonstrationData
              ? "#e4bd57"
              : "#7fa9c2",
            fontWeight: "600",
          }}
        >
          {isDemonstrationData
            ? "DEMO DATA"
            : "BACKEND DATA"}
        </span>
      </div>

      <div
        className="data-status-grid"
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "10px",
          padding: "18px",
        }}
      >
        <div style={cardStyle}>
          <span style={labelStyle}>
            SOURCE
          </span>

          <strong style={valueStyle}>
            {source ??
              "SOURCE UNAVAILABLE"}
          </strong>
        </div>

        <div style={cardStyle}>
          <span style={labelStyle}>
            LAST UPDATED
          </span>

          <strong style={valueStyle}>
            {formatTimestamp(timestamp)}
          </strong>
        </div>

        <div style={cardStyle}>
          <span style={labelStyle}>
            FRESHNESS
          </span>

          <strong style={valueStyle}>
            {freshness.label}
          </strong>
        </div>

        <div style={cardStyle}>
          <span style={labelStyle}>
            DECISION STATUS
          </span>

          <strong style={valueStyle}>
            {status ??
              "UNKNOWN"}
          </strong>
        </div>

        <div style={cardStyle}>
          <span style={labelStyle}>
            CONFIDENCE
          </span>

          <strong style={valueStyle}>
            {confidence !== null &&
            confidence !== undefined
              ? `${confidence}%`
              : "NOT SUPPLIED"}
          </strong>
        </div>

        <div style={cardStyle}>
          <span style={labelStyle}>
            EVIDENCE RECORDS
          </span>

          <strong style={valueStyle}>
            {hasEvidence
              ? evidence.length
              : "NONE"}
          </strong>
        </div>
      </div>

      <div
        style={{
          margin: "0 18px 18px",
          padding: "16px",
          border: isDemonstrationData
            ? "1px solid #6b5722"
            : "1px solid #223b4d",
          borderRadius: "8px",
          background: isDemonstrationData
            ? "#171810"
            : "#0b1722",
        }}
      >
        <strong
          style={{
            display: "block",
            marginBottom: "7px",
            fontSize: "11px",
            letterSpacing: "0.08em",
            color: isDemonstrationData
              ? "#e4bd57"
              : "#7fa9c2",
          }}
        >
          {isDemonstrationData
            ? "DEMONSTRATION DATA"
            : "DATA LINEAGE"}
        </strong>

        <p
          style={{
            margin: 0,
            color: "#aab8c3",
            fontSize: "13px",
            lineHeight: "1.55",
          }}
        >
          {isDemonstrationData
            ? "This information is demonstration data and must not be interpreted as live marine observations."
            : source
              ? `Decision data was supplied by ${source}. M3 displays the supplied provenance without creating new scientific values.`
              : "The backend did not supply a source identifier."}
        </p>
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          gap: "10px",
          margin: "0 18px 18px",
          padding: "13px 15px",
          borderRadius: "7px",
          background: "#0b1722",
          border: "1px solid #223b4d",
          flexWrap: "wrap",
        }}
      >
        <strong
          style={{
            fontSize: "11px",
            letterSpacing: "0.07em",
            color: "#8da2b3",
            whiteSpace: "nowrap",
          }}
        >
          FRESHNESS
        </strong>

        <span
          style={{
            fontSize: "13px",
            lineHeight: "1.45",
            color: "#aab8c3",
          }}
        >
          {freshness.detail}
        </span>
      </div>

      {informationGaps > 0 && (
        <div
          className="data-status-warning"
          role="status"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "6px",
            margin: "0 18px 18px",
            padding: "14px 16px",
            border: "1px solid #6b5722",
            borderRadius: "8px",
            background: "#171810",
          }}
        >
          <strong
            style={{
              fontSize: "11px",
              letterSpacing: "0.08em",
              color: "#e4bd57",
            }}
          >
            INFORMATION GAP
          </strong>

          <span
            style={{
              fontSize: "13px",
              lineHeight: "1.5",
              color: "#aab8c3",
            }}
          >
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