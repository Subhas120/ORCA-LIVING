import { getUncertaintyLevel } from "../../utils/uncertainty";


function UncertaintyPanel({
  uncertainty = {},
}) {
  const score =
    uncertainty.score !== null &&
    uncertainty.score !== undefined
      ? uncertainty.score
      : null;

  const suppliedLevel =
    typeof uncertainty.level === "string" &&
    uncertainty.level.trim()
      ? uncertainty.level
      : null;

  const level =
    suppliedLevel ??
    (
      score !== null
        ? getUncertaintyLevel(score)
        : "NOT SUPPLIED"
    );

  const explanation =
    uncertainty.reason ??
    uncertainty.explanation ??
    (
      score !== null
        ? "Uncertainty score supplied by the authoritative decision service."
        : "Uncertainty information is not currently supplied by the authoritative decision service."
    );


  return (
    <section className="uncertainty-panel">

      <div className="panel-title">

        <span>
          UNCERTAINTY
        </span>

        <span>
          {level}
        </span>

      </div>


      <div className="uncertainty-content">

        <div className="uncertainty-score">

          <div>

            <span>
              UNCERTAINTY
            </span>

            <strong>
              {score !== null
                ? `${score}%`
                : "NOT SUPPLIED"}
            </strong>

          </div>


          <div className="uncertainty-bar">

            <div
              style={{
                width:
                  score !== null
                    ? `${score}%`
                    : "0%",
              }}
            />

          </div>

        </div>


        <div className="uncertainty-explanation">

          <h3>
            How certain is the decision?
          </h3>

          <p>
            {explanation}
          </p>

        </div>


        <div className="uncertainty-note">

          <strong>
            INTERPRETATION
          </strong>

          <span>
            Uncertainty is displayed only when
            supplied by the authoritative decision
            service. M3 does not derive uncertainty
            from confidence or recommendation quality.
          </span>

        </div>

      </div>

    </section>
  );
}


export default UncertaintyPanel;