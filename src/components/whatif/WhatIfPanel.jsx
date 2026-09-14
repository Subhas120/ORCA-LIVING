import { useState } from "react";

function WhatIfPanel() {
  const [waveChange, setWaveChange] = useState(0);
  const [windChange, setWindChange] = useState(0);

  const hasChanges =
    waveChange !== 0 ||
    windChange !== 0;

  return (
    <section
      className="whatif-panel"
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
        <span>
          WHAT-IF
        </span>

        <span>
          COUNTERFACTUAL ANALYSIS
        </span>
      </div>

      <div
        className="whatif-intro"
        style={{
          padding: "0 20px 18px",
        }}
      >
        <h2
          style={{
            marginBottom: "7px",
          }}
        >
          Test a different condition
        </h2>

        <p
          style={{
            margin: 0,
            maxWidth: "760px",
            color: "#91a5b3",
            lineHeight: "1.55",
          }}
        >
          Prepare a hypothetical environmental
          scenario by changing the conditions below.
          The resulting decision must be evaluated by
          the authoritative backend.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "12px",
          padding: "0 18px",
        }}
      >
        <div
          className="scenario-control"
          style={{
            padding: "16px",
            border: "1px solid #223b4d",
            borderRadius: "9px",
            background: "#0f1e2b",
          }}
        >
          <div
            className="scenario-header"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "12px",
              marginBottom: "16px",
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "5px",
              }}
            >
              <strong>
                Wave conditions
              </strong>

              <span
                style={{
                  fontSize: "11px",
                  color: "#718797",
                }}
              >
                Change from current conditions
              </span>
            </div>

            <strong
              style={{
                minWidth: "48px",
                textAlign: "right",
                fontSize: "16px",
                color:
                  waveChange === 0
                    ? "#dce7ed"
                    : "#e4bd57",
              }}
            >
              {waveChange > 0 ? "+" : ""}
              {waveChange}%
            </strong>
          </div>

          <input
            type="range"
            min="-50"
            max="50"
            value={waveChange}
            onChange={(event) =>
              setWaveChange(
                Number(event.target.value)
              )
            }
            aria-label="Wave condition change"
            style={{
              width: "100%",
              cursor: "pointer",
            }}
          />

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginTop: "7px",
              fontSize: "10px",
              color: "#657987",
            }}
          >
            <span>-50%</span>
            <span>Current</span>
            <span>+50%</span>
          </div>
        </div>

        <div
          className="scenario-control"
          style={{
            padding: "16px",
            border: "1px solid #223b4d",
            borderRadius: "9px",
            background: "#0f1e2b",
          }}
        >
          <div
            className="scenario-header"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "12px",
              marginBottom: "16px",
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "5px",
              }}
            >
              <strong>
                Wind conditions
              </strong>

              <span
                style={{
                  fontSize: "11px",
                  color: "#718797",
                }}
              >
                Change from current conditions
              </span>
            </div>

            <strong
              style={{
                minWidth: "48px",
                textAlign: "right",
                fontSize: "16px",
                color:
                  windChange === 0
                    ? "#dce7ed"
                    : "#e4bd57",
              }}
            >
              {windChange > 0 ? "+" : ""}
              {windChange}%
            </strong>
          </div>

          <input
            type="range"
            min="-50"
            max="50"
            value={windChange}
            onChange={(event) =>
              setWindChange(
                Number(event.target.value)
              )
            }
            aria-label="Wind condition change"
            style={{
              width: "100%",
              cursor: "pointer",
            }}
          />

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginTop: "7px",
              fontSize: "10px",
              color: "#657987",
            }}
          >
            <span>-50%</span>
            <span>Current</span>
            <span>+50%</span>
          </div>
        </div>
      </div>

      <div
        className="whatif-result"
        style={{
          margin: "14px 18px 0",
          padding: "16px",
          border: hasChanges
            ? "1px solid #6b5722"
            : "1px solid #223b4d",
          borderRadius: "9px",
          background: hasChanges
            ? "#171810"
            : "#0b1722",
        }}
      >
        <span
          style={{
            display: "block",
            marginBottom: "8px",
            fontSize: "10px",
            fontWeight: "600",
            letterSpacing: "0.09em",
            color: hasChanges
              ? "#e4bd57"
              : "#8da2b3",
          }}
        >
          SCENARIO STATUS
        </span>

        {hasChanges ? (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "7px",
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: "15px",
              }}
            >
              Scenario prepared — evaluation required
            </h3>

            <p
              style={{
                margin: 0,
                fontSize: "12px",
                lineHeight: "1.55",
                color: "#aab8c3",
              }}
            >
              Wave:{" "}
              {waveChange > 0 ? "+" : ""}
              {waveChange}%{" "}
              · Wind:{" "}
              {windChange > 0 ? "+" : ""}
              {windChange}%.
              {" "}
              No new recommendation is calculated
              by M3. An authoritative backend
              counterfactual evaluation is required.
            </p>
          </div>
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "7px",
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: "15px",
              }}
            >
              No scenario changes
            </h3>

            <p
              style={{
                margin: 0,
                fontSize: "12px",
                lineHeight: "1.55",
                color: "#91a5b3",
              }}
            >
              Adjust the conditions above to prepare
              a counterfactual scenario.
            </p>
          </div>
        )}
      </div>

      <div
        className="whatif-warning"
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
          BACKEND EVALUATION REQUIRED
        </strong>

        <span
          style={{
            fontSize: "12px",
            lineHeight: "1.55",
            color: "#91a5b3",
          }}
        >
          M3 only prepares the hypothetical scenario.
          It does not fabricate safety, opportunity,
          confidence, or recommendation results.
          When the backend exposes counterfactual
          analysis, this panel can display the
          authoritative before-and-after result.
        </span>
      </div>
    </section>
  );
}

export default WhatIfPanel;