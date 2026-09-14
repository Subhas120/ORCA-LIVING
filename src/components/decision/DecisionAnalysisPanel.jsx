function formatValue(
  value
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  if (
    typeof value === "object"
  ) {
    return JSON.stringify(
      value
    );
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
    <div className="analysis-section">

      <div className="analysis-section-header">

        <strong>
          {title}
        </strong>

        <span>
          {available
            ? "AVAILABLE"
            : "NOT SUPPLIED"}
        </span>

      </div>


      {available ? (

        <div className="analysis-content">

          {typeof data === "object" ? (

            Object.entries(
              data
            ).map(
              ([key, value]) => (

                <div
                  className="analysis-item"
                  key={key}
                >

                  <span>
                    {key
                      .replace(
                        /_/g,
                        " "
                      )
                      .toUpperCase()}
                  </span>

                  <strong>
                    {formatValue(
                      value
                    )}
                  </strong>

                </div>

              )
            )

          ) : (

            <div className="analysis-item">

              <strong>
                {formatValue(
                  data
                )}
              </strong>

            </div>

          )}

        </div>

      ) : (

        <div className="analysis-unavailable">

          <strong>
            Backend analysis not supplied
          </strong>

          <span>
            M3 does not calculate this result locally.
            It will be displayed when an authoritative
            backend decision service provides it.
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
    Array.isArray(
      informationGaps
    ) &&
    informationGaps.length > 0;


  return (
    <section
      className="decision-analysis-panel"
      aria-labelledby="decision-analysis-title"
    >

      <div className="panel-title">

        <span id="decision-analysis-title">
          DECISION ANALYSIS
        </span>

        <span>
          BACKEND-SUPPLIED RESULTS
        </span>

      </div>


      <div className="analysis-intro">

        <h2>
          Decision robustness & what-if analysis
        </h2>

        <p>
          These views display sensitivity,
          counterfactual and robustness information
          supplied by the decision service. M3 does
          not calculate new decision results.
        </p>

      </div>


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


      {hasInformationGaps && (

        <div
          className="analysis-information-gaps"
          role="status"
        >

          <div className="analysis-section-header">

            <strong>
              INFORMATION GAPS
            </strong>

            <span>
              {informationGaps.length}
            </span>

          </div>


          {informationGaps.map(
            (gap, index) => (

              <p
                key={
                  `${gap}-${index}`
                }
              >
                • {formatValue(gap)}
              </p>

            )
          )}

        </div>

      )}


      <div className="analysis-policy">

        <strong>
          M3 POLICY
        </strong>

        <span>
          No local safety, optimization, dominance,
          sensitivity, counterfactual or robustness
          calculation is performed by this interface.
        </span>

      </div>

    </section>
  );
}


export default DecisionAnalysisPanel;