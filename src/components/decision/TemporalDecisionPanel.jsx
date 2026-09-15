import { useState } from "react";

const TIME_OPTIONS = [
  {
    id: "NOW",
    label: "NOW",
  },
  {
    id: "+6H",
    label: "+6h",
  },
  {
    id: "+12H",
    label: "+12h",
  },
  {
    id: "+24H",
    label: "+24h",
  },
];

function TemporalDecisionPanel({
  currentDecision,
}) {
  const [selectedTime, setSelectedTime] =
    useState("NOW");

  const timeline =
    currentDecision?.timeline ?? {};

  const currentState =
    timeline[selectedTime] ?? null;

  const currentRecommendation =
    currentDecision?.recommendedCandidate ??
    null;

  const isCurrent =
    selectedTime === "NOW";

  return (
    <section className="temporal-panel">
      <div className="panel-title">
        <span>
          TEMPORAL DECISION
        </span>

        <span>
          DECISION CHANGE
        </span>
      </div>

      <div className="temporal-intro">
        <h2>
          How the decision changes over time
        </h2>

        <p>
          Compare decision states across time as
          future marine conditions become available
          from the backend.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(4, minmax(0, 1fr))",
          gap: "10px",
          marginTop: "20px",
        }}
      >
        {TIME_OPTIONS.map((option) => {
          const available =
            option.id === "NOW"
              ? true
              : timeline[option.id] !==
                undefined;

          const selected =
            selectedTime === option.id;

          return (
            <button
              key={option.id}
              type="button"
              onClick={() =>
                setSelectedTime(option.id)
              }
              disabled={!available}
              style={{
                padding: "12px",
                borderRadius: "8px",
                border: selected
                  ? "1px solid #55d69b"
                  : "1px solid #223b4d",
                background: selected
                  ? "#122b25"
                  : "#0f1e2b",
                color: available
                  ? "#d8e4ec"
                  : "#657987",
                cursor: available
                  ? "pointer"
                  : "not-allowed",
                opacity: available
                  ? 1
                  : 0.65,
              }}
            >
              <strong>
                {option.label}
              </strong>

              <div
                style={{
                  marginTop: "5px",
                  fontSize: "11px",
                }}
              >
                {available
                  ? "AVAILABLE"
                  : "BACKEND DATA NEEDED"}
              </div>
            </button>
          );
        })}
      </div>

      <div
        style={{
          marginTop: "20px",
          padding: "18px",
          border: "1px solid #223b4d",
          borderRadius: "9px",
          background: "#0f1e2b",
        }}
      >
        {isCurrent ? (
          <>
            <div
              style={{
                fontSize: "11px",
                letterSpacing: "0.08em",
                color: "#8da2b3",
              }}
            >
              CURRENT DECISION
            </div>

            <h3
              style={{
                margin: "8px 0",
              }}
            >
              {currentRecommendation?.name ??
                "Recommendation unavailable"}
            </h3>

            <p
              style={{
                margin: 0,
                color: "#aab8c3",
                lineHeight: "1.5",
              }}
            >
              {currentDecision
                ?.recommendation
                ?.reason ??
                "No recommendation reason supplied."}
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(3, minmax(0, 1fr))",
                gap: "12px",
                marginTop: "16px",
              }}
            >
              <div>
                <span
                  style={{
                    display: "block",
                    fontSize: "10px",
                    color: "#718797",
                  }}
                >
                  SAFETY
                </span>

                <strong>
                  {currentDecision
                    ?.marineSafety
                    ?.status ??
                    "NOT SUPPLIED"}
                </strong>
              </div>

              <div>
                <span
                  style={{
                    display: "block",
                    fontSize: "10px",
                    color: "#718797",
                  }}
                >
                  CONFIDENCE
                </span>

                <strong>
                  {currentDecision
                    ?.confidence !== null &&
                  currentDecision
                    ?.confidence !== undefined
                    ? `${currentDecision.confidence}%`
                    : "NOT SUPPLIED"}
                </strong>
              </div>

              <div>
                <span
                  style={{
                    display: "block",
                    fontSize: "10px",
                    color: "#718797",
                  }}
                >
                  UNCERTAINTY
                </span>

                <strong>
                  {currentDecision
                    ?.uncertainty
                    ?.score !== null &&
                  currentDecision
                    ?.uncertainty
                    ?.score !== undefined
                    ? `${currentDecision.uncertainty.score}%`
                    : "NOT SUPPLIED"}
                </strong>
              </div>
            </div>
          </>
        ) : currentState ? (
          <>
            <div
              style={{
                fontSize: "11px",
                letterSpacing: "0.08em",
                color: "#8da2b3",
              }}
            >
              FUTURE DECISION STATE
            </div>

            <h3
              style={{
                margin: "8px 0",
              }}
            >
              {currentState.recommendedCandidate
                ?.name ??
                "Recommendation unavailable"}
            </h3>

            <p
              style={{
                margin: 0,
                color: "#aab8c3",
                lineHeight: "1.5",
              }}
            >
              {currentState.recommendation
                ?.reason ??
                "Backend supplied future decision state."}
            </p>
          </>
        ) : (
          <>
            <div
              style={{
                fontSize: "11px",
                letterSpacing: "0.08em",
                color: "#e4bd57",
              }}
            >
              FUTURE DATA UNAVAILABLE
            </div>

            <h3
              style={{
                margin: "8px 0",
              }}
            >
              Backend temporal data required
            </h3>

            <p
              style={{
                margin: 0,
                color: "#aab8c3",
                lineHeight: "1.5",
              }}
            >
              The M4 decision service currently
              supplies the present decision only.
              M3 does not generate or predict
              +6h, +12h, or +24h decisions locally.
              Future states will appear here when the
              backend provides authoritative temporal
              decision data.
            </p>
          </>
        )}
      </div>

      <div
        style={{
          marginTop: "16px",
          padding: "14px 16px",
          border: "1px solid #223b4d",
          borderRadius: "8px",
          background: "#0b1722",
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
          DECISION-CHANGE RULE
        </strong>

        <span
          style={{
            fontSize: "13px",
            lineHeight: "1.5",
            color: "#aab8c3",
          }}
        >
          A decision change is displayed only when
          the backend supplies a different temporal
          decision state. M3 does not calculate future
          safety, opportunity, confidence, or rankings.
        </span>
      </div>
    </section>
  );
}

export default TemporalDecisionPanel;