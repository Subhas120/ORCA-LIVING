const DECISION_STATES = {
  RECOMMENDED: {
    title: "RECOMMENDED",
    description:
      "This candidate was explicitly identified by the decision service as the recommendation.",
  },

  ALTERNATIVE: {
    title: "ALTERNATIVE",
    description:
      "This candidate was explicitly identified by the decision service as an alternative.",
  },

  UNSAFE: {
    title: "UNSAFE",
    description:
      "The decision service explicitly marked this candidate as unsafe.",
  },

  INSUFFICIENT_EVIDENCE: {
    title: "INSUFFICIENT EVIDENCE",
    description:
      "There is not enough evidence to support a reliable decision for this candidate.",
  },

  DOMINATED: {
    title: "DOMINATED",
    description:
      "The decision service explicitly identified this candidate as dominated.",
  },

  REJECTED: {
    title: "REJECTED",
    description:
      "The decision service explicitly rejected this candidate.",
  },
};

function DecisionStatusPanel({
  candidate = null,
  decision = {},
}) {
  const candidateStatus =
    candidate?.status ?? null;

  const normalizedStatus =
    typeof candidateStatus === "string"
      ? candidateStatus
          .trim()
          .toUpperCase()
          .replace(/[\s-]+/g, "_")
      : null;

  const statusInfo =
    DECISION_STATES[normalizedStatus];

  const marineSafetyStatus =
    decision?.marineSafety?.status ?? null;

  const reasons =
    Array.isArray(candidate?.rejectionReasons)
      ? candidate.rejectionReasons
      : [];

  const informationGaps =
    Array.isArray(candidate?.informationGaps)
      ? candidate.informationGaps
      : [];

  const reason =
    candidate?.rejectionReason ??
    candidate?.reason ??
    null;

  const noSafeAction =
    normalizedStatus === "UNSAFE" ||
    normalizedStatus === "INSUFFICIENT_EVIDENCE" ||
    (!candidate &&
      (marineSafetyStatus === "UNSAFE" ||
        marineSafetyStatus ===
          "INSUFFICIENT_EVIDENCE"));

  const statusTitle =
    statusInfo?.title ??
    candidateStatus ??
    "UNKNOWN";

  return (
    <section
      className="decision-status-panel"
      aria-labelledby="decision-status-title"
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
        <span id="decision-status-title">
          DECISION STATUS
        </span>

        <span
          style={{
            color:
              normalizedStatus === "RECOMMENDED"
                ? "#78d6a5"
                : normalizedStatus ===
                    "UNSAFE"
                  ? "#ef767a"
                  : "#8da2b3",
            fontWeight: "600",
          }}
        >
          {statusTitle}
        </span>
      </div>

      {noSafeAction && (
        <div
          className="no-safe-action"
          role="alert"
          style={{
            margin: "18px",
            padding: "15px 16px",
            border: "1px solid #7a3438",
            borderRadius: "8px",
            background: "#211416",
            display: "flex",
            flexDirection: "column",
            gap: "7px",
          }}
        >
          <strong
            style={{
              fontSize: "11px",
              letterSpacing: "0.08em",
              color: "#ef767a",
            }}
          >
            NO SAFE ACTION CONFIRMED
          </strong>

          <span
            style={{
              fontSize: "13px",
              lineHeight: "1.5",
              color: "#b9c4cb",
            }}
          >
            The available decision information does
            not identify a safe action for this state.
          </span>
        </div>
      )}

      <div
        className="decision-status-content"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          padding: "18px",
        }}
      >
        <div
          className="decision-status-main"
          style={{
            padding: "18px",
            border: "1px solid #223b4d",
            borderRadius: "9px",
            background: "#0f1e2b",
          }}
        >
          <span
            style={{
              display: "block",
              marginBottom: "8px",
              fontSize: "10px",
              fontWeight: "600",
              letterSpacing: "0.09em",
              color: "#7691a4",
            }}
          >
            CANDIDATE STATUS
          </span>

          <h2
            style={{
              margin: "0 0 8px",
              fontSize: "25px",
            }}
          >
            {statusTitle}
          </h2>

          <p
            style={{
              margin: 0,
              maxWidth: "800px",
              fontSize: "13px",
              lineHeight: "1.55",
              color: "#aab8c3",
            }}
          >
            {statusInfo?.description ??
              "No semantic decision state was supplied for this candidate."}
          </p>
        </div>

        {reason && (
          <div
            className="decision-status-reason"
            style={{
              padding: "15px 16px",
              border: "1px solid #223b4d",
              borderRadius: "8px",
              background: "#0b1722",
            }}
          >
            <span
              style={{
                display: "block",
                marginBottom: "7px",
                fontSize: "10px",
                fontWeight: "600",
                letterSpacing: "0.08em",
                color: "#7691a4",
              }}
            >
              REASON
            </span>

            <p
              style={{
                margin: 0,
                fontSize: "13px",
                lineHeight: "1.5",
                color: "#c4d0d7",
              }}
            >
              {reason}
            </p>
          </div>
        )}

        {reasons.length > 0 && (
          <div
            className="decision-status-reasons"
            style={{
              padding: "15px 16px",
              border: "1px solid #223b4d",
              borderRadius: "8px",
              background: "#0b1722",
            }}
          >
            <span
              style={{
                display: "block",
                marginBottom: "9px",
                fontSize: "10px",
                fontWeight: "600",
                letterSpacing: "0.08em",
                color: "#7691a4",
              }}
            >
              REJECTION REASONS
            </span>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
            >
              {reasons.map(
                (item, index) => (
                  <p
                    key={`${item}-${index}`}
                    style={{
                      margin: 0,
                      fontSize: "13px",
                      lineHeight: "1.5",
                      color: "#aab8c3",
                    }}
                  >
                    • {item}
                  </p>
                )
              )}
            </div>
          </div>
        )}

        {informationGaps.length > 0 && (
          <div
            className="decision-status-gaps"
            style={{
              padding: "15px 16px",
              border: "1px solid #6b5722",
              borderRadius: "8px",
              background: "#171810",
            }}
          >
            <span
              style={{
                display: "block",
                marginBottom: "9px",
                fontSize: "10px",
                fontWeight: "600",
                letterSpacing: "0.08em",
                color: "#e4bd57",
              }}
            >
              INFORMATION GAPS
            </span>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
            >
              {informationGaps.map(
                (item, index) => (
                  <p
                    key={`${item}-${index}`}
                    style={{
                      margin: 0,
                      fontSize: "13px",
                      lineHeight: "1.5",
                      color: "#aab8c3",
                    }}
                  >
                    • {item}
                  </p>
                )
              )}
            </div>
          </div>
        )}
      </div>

      <div
        className="decision-status-source"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
          margin: "0 18px 12px",
          padding: "14px 16px",
          border: "1px solid #223b4d",
          borderRadius: "8px",
          background: "#0f1e2b",
          flexWrap: "wrap",
        }}
      >
        <span
          style={{
            fontSize: "10px",
            fontWeight: "600",
            letterSpacing: "0.08em",
            color: "#7691a4",
          }}
        >
          MARINE SAFETY STATUS
        </span>

        <strong
          style={{
            fontSize: "13px",
            color: marineSafetyStatus
              ? "#dce7ed"
              : "#e4bd57",
          }}
        >
          {marineSafetyStatus ??
            "NOT SUPPLIED"}
        </strong>
      </div>

      <div
        className="decision-status-note"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "7px",
          margin: "0 18px 18px",
          padding: "15px 16px",
          border: "1px solid #223b4d",
          borderRadius: "8px",
          background: "#0b1722",
        }}
      >
        <strong
          style={{
            fontSize: "11px",
            letterSpacing: "0.08em",
            color: "#8da2b3",
          }}
        >
          M3 DISPLAY POLICY
        </strong>

        <span
          style={{
            fontSize: "12px",
            lineHeight: "1.55",
            color: "#91a5b3",
          }}
        >
          M3 displays semantic decision states supplied
          by the backend. It does not calculate safety,
          ranking, dominance, or suitability locally.
        </span>
      </div>
    </section>
  );
}

export default DecisionStatusPanel;