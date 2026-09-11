import { decisionState } from "./models/decisionState";
import { candidates } from "./data/mockDecision";
import MarineMap from "./components/map/MarineMap";

function App() {
  const recommended = decisionState.recommendedCandidate;

  return (
    <div className="app">

      <header className="header">
        <div>
          <h1>ORCA-LIVING</h1>
          <p>Marine Decision Intelligence</p>
        </div>

        <div className="data-mode">
          ● {decisionState.dataMode}
        </div>
      </header>

      <main className="dashboard">

        <section className="objective">
          <span>USER OBJECTIVE</span>

          <h2>{decisionState.objective.text}</h2>

          <p>
            Vessel: {decisionState.objective.vessel} ·{" "}
            {decisionState.objective.time}
          </p>
        </section>

        <section className="content-grid">

          {/* REAL LEAFLET MAP */}

          <div className="map-panel">

            <div className="panel-title">
              <span>MARINE MAP</span>
              <span>{candidates.length} CANDIDATES</span>
            </div>

            <MarineMap candidates={candidates} />

          </div>


          {/* DECISION PANEL */}

          <div className="decision-panel">

            <div className="panel-title">
              <span>DECISION</span>

              <span className="confidence">
                {recommended.confidence}
              </span>
            </div>


            <div className="recommendation">

              <span>RECOMMENDED</span>

              <h2>{recommended.name}</h2>

              <p>
                {decisionState.decisionSummary}
              </p>

            </div>


            <div className="metrics">

              <div>
                <span>SAFETY</span>
                <strong>{recommended.safety}%</strong>
              </div>

              <div>
                <span>OPPORTUNITY</span>
                <strong>{recommended.opportunity}%</strong>
              </div>

              <div>
                <span>UNCERTAINTY</span>
                <strong>{recommended.uncertainty}%</strong>
              </div>

              <div>
                <span>DISTANCE</span>
                <strong>{recommended.distance} km</strong>
              </div>

            </div>


            <div className="why">

              <h3>WHY?</h3>

              {decisionState.tradeoffs.map((tradeoff) => (
                <p key={tradeoff}>
                  ✓ {tradeoff}
                </p>
              ))}

            </div>

          </div>

        </section>


        {/* CANDIDATES */}

        <section className="candidates">

          <div className="section-heading">

            <h2>Candidates</h2>

            <span>
              DECISION FRONTIER
            </span>

          </div>


          <div className="candidate-grid">

            {candidates.map((candidate) => (

              <div
                key={candidate.id}
                className={`candidate-card ${candidate.status.toLowerCase()}`}
              >

                <div className="candidate-header">

                  <h3>
                    {candidate.name}
                  </h3>

                  <span>
                    {candidate.status}
                  </span>

                </div>


                <div className="candidate-stats">

                  <div>
                    <small>Safety</small>
                    <strong>{candidate.safety}%</strong>
                  </div>

                  <div>
                    <small>Opportunity</small>
                    <strong>{candidate.opportunity}%</strong>
                  </div>

                  <div>
                    <small>Uncertainty</small>
                    <strong>{candidate.uncertainty}%</strong>
                  </div>

                  <div>
                    <small>Distance</small>
                    <strong>{candidate.distance} km</strong>
                  </div>

                </div>


                <p className="candidate-reason">
                  {candidate.reason}
                </p>

              </div>

            ))}

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;