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
    candidate?.status ??
    null;


  const normalizedStatus =
    typeof candidateStatus === "string"
      ? candidateStatus
          .trim()
          .toUpperCase()
          .replace(
            /[\s-]+/g,
            "_"
          )
      : null;


  const statusInfo =
    DECISION_STATES[
      normalizedStatus
    ];


  const marineSafetyStatus =
    decision?.marineSafety?.status ??
    null;


  const reasons =
    Array.isArray(
      candidate?.rejectionReasons
    )
      ? candidate.rejectionReasons
      : [];


  const informationGaps =
    Array.isArray(
      candidate?.informationGaps
    )
      ? candidate.informationGaps
      : [];


  const reason =
    candidate?.rejectionReason ??
    candidate?.reason ??
    null;


  const noSafeAction =
    normalizedStatus ===
      "UNSAFE" ||
    normalizedStatus ===
      "INSUFFICIENT_EVIDENCE" ||
    (
      !candidate &&
      (
        marineSafetyStatus ===
          "UNSAFE" ||
        marineSafetyStatus ===
          "INSUFFICIENT_EVIDENCE"
      )
    );


  return (
    <section
      className="decision-status-panel"
      aria-labelledby="decision-status-title"
    >

      <div className="panel-title">

        <span id="decision-status-title">
          DECISION STATUS
        </span>

        <span>
          {statusInfo?.title ??
            "UNKNOWN"}
        </span>

      </div>


      {noSafeAction && (

        <div
          className="no-safe-action"
          role="alert"
        >

          <strong>
            NO SAFE ACTION CONFIRMED
          </strong>

          <span>
            The available decision information does
            not identify a safe action for this state.
          </span>

        </div>

      )}


      <div className="decision-status-content">

        <div className="decision-status-main">

          <span>
            CANDIDATE STATUS
          </span>

          <h2>
            {statusInfo?.title ??
              candidateStatus ??
              "UNKNOWN"}
          </h2>

          <p>
            {statusInfo?.description ??
              "No semantic decision state was supplied for this candidate."}
          </p>

        </div>


        {reason && (

          <div className="decision-status-reason">

            <span>
              REASON
            </span>

            <p>
              {reason}
            </p>

          </div>

        )}


        {reasons.length > 0 && (

          <div className="decision-status-reasons">

            <span>
              REJECTION REASONS
            </span>

            {reasons.map(
              (item, index) => (

                <p
                  key={
                    `${item}-${index}`
                  }
                >
                  • {item}
                </p>

              )
            )}

          </div>

        )}


        {informationGaps.length > 0 && (

          <div className="decision-status-gaps">

            <span>
              INFORMATION GAPS
            </span>

            {informationGaps.map(
              (item, index) => (

                <p
                  key={
                    `${item}-${index}`
                  }
                >
                  • {item}
                </p>

              )
            )}

          </div>

        )}

      </div>


      <div className="decision-status-source">

        <span>
          MARINE SAFETY STATUS
        </span>

        <strong>
          {marineSafetyStatus ??
            "NOT SUPPLIED"}
        </strong>

      </div>


      <div className="decision-status-note">

        <strong>
          M3 DISPLAY POLICY
        </strong>

        <span>
          M3 displays semantic decision states supplied
          by the backend. It does not calculate safety,
          ranking, dominance, or suitability locally.
        </span>

      </div>

    </section>
  );
}


export default DecisionStatusPanel;
