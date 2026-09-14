import { decisionState } from "../../models/decisionState";
import { getUncertaintyLevel } from "../../utils/uncertainty";

function UncertaintyPanel() {
  const uncertainty = decisionState.uncertainty;

  /*
   * Backend-provided uncertainty level is authoritative.
   *
   * If a future backend response contains only a score,
   * use the utility as a frontend fallback.
   */
  const level =
    uncertainty.level ||
    getUncertaintyLevel(uncertainty.score);

  return (
    <section className="uncertainty-panel">

      <div className="panel-title">
        <span>UNCERTAINTY</span>

        <span>
          {level}
        </span>
      </div>


      <div className="uncertainty-content">

        {/* SCORE */}

        <div className="uncertainty-score">

          <div>
            <span>
              UNCERTAINTY SCORE
            </span>

            <strong>
              {uncertainty.score}%
            </strong>
          </div>


          <div className="uncertainty-bar">

            <div
              style={{
                width: `${uncertainty.score}%`,
              }}
            />

          </div>

        </div>


        {/* EXPLANATION */}

        <div className="uncertainty-explanation">

          <h3>
            How certain is the decision?
          </h3>

          <p>
            {uncertainty.explanation}
          </p>

        </div>


        {/* INTERPRETATION */}

        <div className="uncertainty-note">

          <strong>
            INTERPRETATION
          </strong>

          <span>
            Lower uncertainty means the available
            evidence is more consistent. This value
            represents uncertainty, not recommendation
            quality.
          </span>

        </div>

      </div>

    </section>
  );
}

export default UncertaintyPanel;