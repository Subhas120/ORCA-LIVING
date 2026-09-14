import { useState } from "react";


function WhatIfPanel() {
  const [waveChange, setWaveChange] = useState(0);
  const [windChange, setWindChange] = useState(0);


  const hasChanges =
    waveChange !== 0 ||
    windChange !== 0;


  return (
    <section className="whatif-panel">

      <div className="panel-title">

        <span>
          WHAT-IF
        </span>

        <span>
          COUNTERFACTUAL ANALYSIS
        </span>

      </div>


      <div className="whatif-intro">

        <h2>
          Test a different condition
        </h2>

        <p>
          Explore how changing environmental
          conditions could affect the current
          decision.
        </p>

      </div>


      <div className="scenario-control">

        <div className="scenario-header">

          <div>

            <strong>
              Wave conditions
            </strong>

            <span>
              Change from current conditions
            </span>

          </div>


          <strong>
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
        />

      </div>


      <div className="scenario-control">

        <div className="scenario-header">

          <div>

            <strong>
              Wind conditions
            </strong>

            <span>
              Change from current conditions
            </span>

          </div>


          <strong>
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
        />

      </div>


      <div className="whatif-result">

        <span>
          SCENARIO STATUS
        </span>


        {hasChanges ? (

          <div>

            <h3>
              Backend counterfactual evaluation required
            </h3>

            <p>
              The scenario has been prepared, but M3
              does not calculate a new recommendation
              locally. A backend counterfactual endpoint
              is required before a changed decision can
              be reported.
            </p>

          </div>

        ) : (

          <div>

            <h3>
              No scenario changes
            </h3>

            <p>
              Adjust the conditions above to prepare
              a counterfactual scenario.
            </p>

          </div>

        )}

      </div>


      <div className="whatif-warning">

        <strong>
          NO LOCAL DECISION CALCULATION
        </strong>

        <span>
          M3 will not fabricate safety, opportunity,
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