import { getUncertaintyLevel } from "../../utils/uncertainty";


function UncertaintyPanel({
  uncertainty = {},
}) {
  const score =
    uncertainty.score ??
    null;

  const level =
    uncertainty.level ??
    (
      score !== null
        ? getUncertaintyLevel(score)
        : "INSUFFICIENT"
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
                : "—"}
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
            {uncertainty.reason ??
              "Uncertainty information is not currently available from the backend."}
          </p>

        </div>


        <div className="uncertainty-note">

          <strong>
            INTERPRETATION
          </strong>

          <span>
            Lower uncertainty indicates more
            consistent evidence. Uncertainty is
            separate from recommendation quality.
          </span>

        </div>

      </div>

    </section>
  );
}


export default UncertaintyPanel;