function formatValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function AnalysisSection({
  title,
  data,
}) {
  const available =
    data !== null &&
    data !== undefined;

  return (
    <div
      className="analysis-section"
      style={{
        border: "1px solid #223b4d",
        borderRadius: "9px",
        background: "#0f1e2b",
        overflow: "hidden",
      }}
    >
      <div
        className="analysis-section-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "12px",
          padding: "14px 16px",
          borderBottom: "1px solid #223b4d",
        }}
      >
        <strong
          style={{
            fontSize: "12px",
            letterSpacing: "0.08em",
          }}
        >
          {title}
        </strong>

        <span
          style={{
            padding: "4px 8px",
            borderRadius: "5px",
            fontSize: "9px",
            fontWeight: "700",
            letterSpacing: "0.06em",
            color: available
              ? "#78d6a5"
              : "#e4bd57",
            background: available
              ? "#10291f"
              : "#252014",
            border: available
              ? "1px solid #28553f"
              : "1px solid #5a4a20",
            whiteSpace: "nowrap",
          }}
        >
          {available
            ? "AVAILABLE"
            : "NOT SUPPLIED"}
        </span>
      </div>

      {available ? (
        <div
          className="analysis-content"
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "10px",
            padding: "14px",
          }}
        >
          {typeof data === "object" ? (
            Object.entries(data).map(
              ([key, value]) => (
                <div
                  className="analysis-item"
                  key={key}
                  style={{
                    padding: "13px",
                    borderRadius: "7px",
                    background: "#0b1722",
                    border: "1px solid #1d3444",
                    minWidth: 0,
                  }}
                >
                  <span
                    style={{
                      display: "block",
                      marginBottom: "6px",
                      fontSize: "9px",
                      fontWeight: "600",
                      letterSpacing: "0.08em",
                      color: "#718797",
                    }}
                  >
                    {key
                      .replace(
                        /_/g,
                        " "
                      )
                      .toUpperCase()}
                  </span>

                  <strong
                    style={{
                      display: "block",
                      fontSize: "13px",
                      lineHeight: "1.45",
                      color: "#dce7ed",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {formatValue(value)}
                  </strong>
                </div>
              )
            )
          ) : (
            <div
              className="analysis-item"
              style={{
                padding: "13px",
                borderRadius: "7px",
                background: "#0b1722",
                border: "1px solid #1d3444",
              }}
            >
              <strong
                style={{
                  fontSize: "13px",
                  color: "#dce7ed",
                }}
              >
                {formatValue(data)}
              </strong>
            </div>
          )}
        </div>
      ) : (
        <div
          className="analysis-unavailable"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "7px",
            padding: "16px",
            background: "#101b24",
          }}
        >
          <strong
            style={{
              fontSize: "13px",
              color: "#e4bd57",
            }}
          >
            Result not supplied by backend
          </strong>

          <span
            style={{
              fontSize: "12px",
              lineHeight: "1.5",
              color: "#91a5b3",
            }}
          >
            No authoritative {title.toLowerCase()} result
            was provided by the decision service.
            M3 does not calculate this result locally.
          </span>
        </div>
      )}
    </div>
  );
}

function DecisionAnalysisPanel({
  sensitivity = null,
  counterfactual = null,
  robustness = null,
  informationGaps = [],
}) {
  const hasInformationGaps =
    Array.isArray(informationGaps) &&
    informationGaps.length > 0;

  return (
    <section
      className="decision-analysis-panel"
      aria-labelledby="decision-analysis-title"
      style={{
        marginTop: "24px",
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
        }}
      >
        <span id="decision-analysis-title">
          DECISION ANALYSIS
        </span>

        <span>
          BACKEND-SUPPLIED RESULTS
        </span>
      </div>

      <div
        className="analysis-intro"
        style={{
          padding: "0 20px 18px",
        }}
      >
        <h2
          style={{
            marginBottom: "7px",
          }}
        >
          Decision robustness &amp; what-if analysis
        </h2>

        <p
          style={{
            margin: 0,
            maxWidth: "760px",
            color: "#91a5b3",
            lineHeight: "1.55",
          }}
        >
          These views display sensitivity,
          counterfactual and robustness information
          supplied by the decision service. M3 does
          not calculate new decision results.
        </p>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          padding: "0 18px",
        }}
      >
        <AnalysisSection
          title="SENSITIVITY"
          data={sensitivity}
        />

        <AnalysisSection
          title="COUNTERFACTUAL"
          data={counterfactual}
        />

        <AnalysisSection
          title="ROBUSTNESS"
          data={robustness}
        />
      </div>

      {hasInformationGaps && (
        <div
          className="analysis-information-gaps"
          role="status"
          style={{
            margin: "14px 18px 0",
            padding: "15px 16px",
            border: "1px solid #6b5722",
            borderRadius: "8px",
            background: "#171810",
          }}
        >
          <div
            className="analysis-section-header"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "12px",
              marginBottom: "10px",
            }}
          >
            <strong
              style={{
                fontSize: "11px",
                letterSpacing: "0.08em",
                color: "#e4bd57",
              }}
            >
              INFORMATION GAPS
            </strong>

            <span
              style={{
                fontSize: "12px",
                color: "#e4bd57",
              }}
            >
              {informationGaps.length}
            </span>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "6px",
            }}
          >
            {informationGaps.map(
              (gap, index) => (
                <p
                  key={`${gap}-${index}`}
                  style={{
                    margin: 0,
                    fontSize: "12px",
                    lineHeight: "1.5",
                    color: "#aab8c3",
                  }}
                >
                  • {formatValue(gap)}
                </p>
              )
            )}
          </div>
        </div>
      )}

      <div
        className="analysis-policy"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "7px",
          margin: "14px 18px 18px",
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
          This interface displays authoritative
          backend decision intelligence. It does not
          perform local safety, optimization,
          dominance, sensitivity, counterfactual or
          robustness calculations.
        </span>
      </div>
    </section>
  );
}

export default DecisionAnalysisPanel;