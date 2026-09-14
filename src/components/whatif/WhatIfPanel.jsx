import { useState } from "react";

function WhatIfPanel() {
  const [waveChange, setWaveChange] = useState(0);
  const [windChange, setWindChange] = useState(0);

  const hasChanges =
    waveChange !== 0 || windChange !== 0;

  return (
    <section className="whatif-panel">

      <div className="panel-title">
        <span>WHAT-IF</span>
        <span>SCENARIO ANALYSIS</span>
      </div>

      <div className="whatif-intro">
        <h2>Test a different condition</h2>

        <p>
          Change environmental conditions to evaluate
          how the current decision may be affected.
        </p>
      </div>

      <div className="scenario-control">

        <div className="scenario-header">

          <div>
            <strong>Wave conditions</strong>

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
            <strong>Wind conditions</strong>

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

        <span>SCENARIO RESULT</span>

        {hasChanges ? (

          <div>
            <h3>
              Waiting for live decision model
            </h3>

            <p>
              The selected scenario will be evaluated
              using the real-time backend once the
              decision API is connected.
            </p>
          </div>

        ) : (

          <div>
            <h3>No scenario changes</h3>

            <p>
              Adjust the conditions above to create
              a what-if scenario.
            </p>
          </div>

        )}

      </div>

      <div className="whatif-warning">

        <strong>LIVE DATA REQUIRED</strong>

        <span>
          Scenario results are not generated locally.
          ORCA will use the authoritative backend
          decision model when the API is connected.
        </span>

      </div>

    </section>
  );
}

export default WhatIfPanel;