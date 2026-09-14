import { useEffect, useState } from "react";

import { decisionState as demoDecisionState } from "./models/decisionState";
import { candidates as demoCandidates } from "./data/mockDecision";

import { getDecision } from "./services/decisionService";

import MarineMap from "./components/map/MarineMap";
import EvidencePanel from "./components/evidence/EvidencePanel";
import WhatIfPanel from "./components/whatif/WhatIfPanel";
import UncertaintyPanel from "./components/decision/UncertaintyPanel";
import MarineConditions from "./components/decision/MarineConditions";


function App() {
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  useEffect(() => {
    const endpoint =
      import.meta.env.VITE_ORCA_OCEAN_ENDPOINT;

    if (!endpoint) {
      return;
    }

    async function loadDecision() {
      try {
        setLoading(true);
        setError(null);

        const result = await getDecision({
          query:
            demoDecisionState.objective.text,

          location: null,

          destination: null,

          date: null,

          time:
            demoDecisionState.objective.time,

          activity: "fishing",
        });

        setDecision(result);

      } catch (err) {
        console.error(err);

        setError(
          err.message ||
          "Unable to load ORCA decision."
        );

      } finally {
        setLoading(false);
      }
    }

    loadDecision();

  }, []);


  const usingM2 =
    decision !== null;


  const currentDecision =
    usingM2
      ? decision
      : demoDecisionState;


  const currentCandidates =
    usingM2
      ? decision.candidates
      : demoCandidates;


  const recommended =
    usingM2
      ? decision.recommendedCandidate
      : demoDecisionState.recommendedCandidate;


  const uncertaintyScore =
    usingM2
      ? (
        currentDecision.uncertainty?.score !== null &&
        currentDecision.uncertainty?.score !== undefined
          ? currentDecision.uncertainty.score
          : currentDecision.confidence !== null &&
            currentDecision.confidence !== undefined
            ? 100 - currentDecision.confidence
            : null
      )
      : recommended?.uncertainty ?? null;


  return (
    <div className="app">

      <header className="header">

        <div>

          <h1>
            ORCA-LIVING
          </h1>

          <p>
            Marine Decision Intelligence
          </p>

        </div>


        <div className="data-mode">

          ●{" "}

          {usingM2
            ? "M2 BACKEND CONNECTED"
            : "SIMULATED DEMO"}

        </div>

      </header>


      <main className="dashboard">


        {loading && (

          <section className="integration-status">

            <strong>
              CONNECTING TO ORCA BACKEND
            </strong>

            <span>
              Loading the latest marine decision...
            </span>

          </section>

        )}


        {error && (

          <section className="integration-status error">

            <strong>
              BACKEND UNAVAILABLE
            </strong>

            <span>
              {error}
            </span>

          </section>

        )}


        {!usingM2 &&
          !loading &&
          !error && (

            <section className="integration-status demo">

              <strong>
                DEMO MODE
              </strong>

              <span>
                M2 HTTP endpoint is not configured.
                The dashboard is displaying clearly
                labelled simulated demonstration data.
              </span>

            </section>

          )}


        {error &&
          !loading && (

            <section className="integration-status demo">

              <strong>
                SIMULATED FALLBACK
              </strong>

              <span>
                The M2 backend could not be reached.
                The dashboard is displaying clearly
                labelled simulated demonstration data.
              </span>

            </section>

          )}


        <section className="objective">

          <span>
            USER OBJECTIVE
          </span>

          <h2>
            {demoDecisionState.objective.text}
          </h2>

          <p>
            Vessel:{" "}
            {demoDecisionState.objective.vessel}
            {" · "}
            {demoDecisionState.objective.time}
          </p>

        </section>


        <section className="content-grid">


          <div className="map-panel">

            <div className="panel-title">

              <span>
                MARINE MAP
              </span>

              <span>
                {currentCandidates.length}
                {" "}CANDIDATES
              </span>

            </div>


            <MarineMap
              candidates={
                currentCandidates
              }
            />

          </div>


          <div className="decision-panel">

            <div className="panel-title">

              <span>
                DECISION
              </span>

              <span className="confidence">

                {usingM2
                  ? (
                    currentDecision.confidence !== null
                      ? `${currentDecision.confidence}%`
                      : "UNKNOWN"
                  )
                  : recommended.confidence}

              </span>

            </div>


            <div className="recommendation">

              <span>
                RECOMMENDED
              </span>

              <h2>
                {recommended?.name ??
                  "No recommendation"}
              </h2>

              <p>

                {usingM2
                  ? (
                    currentDecision.recommendation
                      ?.reason ??
                    "Recommendation reason unavailable."
                  )
                  : demoDecisionState.decisionSummary}

              </p>

            </div>


            {usingM2 && (

              <div className="marine-safety">

                <span>
                  MARINE SAFETY
                </span>

                <strong>
                  {currentDecision.marineSafety.status}
                </strong>

                {currentDecision.marineSafety
                  .reasons?.map(
                    (reason) => (

                      <p key={reason}>
                        {reason}
                      </p>

                    )
                  )}

              </div>

            )}


            <div className="metrics">


              <div>

                <span>
                  SAFETY
                </span>

                <strong>

                  {usingM2
                    ? (
                      currentDecision.marineSafety
                        .status ?? "—"
                    )
                    : `${recommended.safety}%`}

                </strong>

              </div>


              <div>

                <span>
                  OPPORTUNITY
                </span>

                <strong>

                  {usingM2
                    ? (
                      recommended.opportunityStatus
                        ?.replace(
                          "_",
                          " "
                        ) ?? "—"
                    )
                    : `${recommended.opportunity}%`}

                </strong>

              </div>


              <div>

                <span>
                  UNCERTAINTY
                </span>

                <strong>

                  {uncertaintyScore !== null &&
                  uncertaintyScore !== undefined
                    ? `${uncertaintyScore}%`
                    : "—"}

                </strong>

              </div>


              <div>

                <span>
                  DISTANCE
                </span>

                <strong>

                  {recommended?.distance !== null &&
                  recommended?.distance !== undefined
                    ? `${recommended.distance} km`
                    : "—"}

                </strong>

              </div>

            </div>


            <div className="why">

              <h3>
                WHY?
              </h3>


              {usingM2 ? (

                currentDecision.recommendation
                  ?.reason ? (

                  <p>
                    ✓{" "}
                    {currentDecision.recommendation.reason}
                  </p>

                ) : (

                  <p>
                    No recommendation reason
                    available.
                  </p>

                )

              ) : (

                demoDecisionState.tradeoffs.map(
                  (tradeoff) => (

                    <p key={tradeoff}>
                      ✓ {tradeoff}
                    </p>

                  )
                )

              )}

            </div>

          </div>

        </section>


        <MarineConditions
          conditions={
            usingM2
              ? currentDecision.marineConditions
              : demoDecisionState.marineConditions
          }

          safety={
            usingM2
              ? currentDecision.marineSafety
              : null
          }
        />


        <section className="candidates">

          <div className="section-heading">

            <h2>
              Candidates
            </h2>

            <span>
              PFZ LOCATIONS
            </span>

          </div>


          <div className="candidate-grid">

            {currentCandidates.map(
              (candidate) => (

                <div
                  key={candidate.id}
                  className={`candidate-card ${
                    candidate.status.toLowerCase()
                  }`}
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

                      <small>
                        Distance
                      </small>

                      <strong>
                        {candidate.distance ??
                          "—"} km
                      </strong>

                    </div>


                    <div>

                      <small>
                        Opportunity
                      </small>

                      <strong>

                        {usingM2
                          ? (
                            candidate.opportunityStatus ??
                            "—"
                          )
                          : `${candidate.opportunity}%`}

                      </strong>

                    </div>


                    <div>

                      <small>
                        Confidence
                      </small>

                      <strong>

                        {candidate.confidence !== null &&
                        candidate.confidence !== undefined
                          ? `${candidate.confidence}%`
                          : "—"}

                      </strong>

                    </div>


                    <div>

                      <small>
                        Location
                      </small>

                      <strong>

                        {candidate.lat !== undefined &&
                        candidate.lng !== undefined
                          ? (
                            <>
                              {candidate.lat.toFixed(2)}
                              {"°, "}
                              {candidate.lng.toFixed(2)}
                              {"°"}
                            </>
                          )
                          : "—"}

                      </strong>

                    </div>

                  </div>


                  <p className="candidate-reason">

                    {candidate.reason ??
                      candidate.opportunityStatus ??
                      ""}

                  </p>

                </div>

              )
            )}

          </div>

        </section>


        <EvidencePanel

          candidate={recommended}

          evidence={
            usingM2
              ? currentDecision.evidence
              : demoDecisionState.evidence
          }

          dataMode={
            usingM2
              ? "M2 BACKEND"
              : demoDecisionState.dataMode
          }

        />


        <UncertaintyPanel

          uncertainty={
            usingM2
              ? {
                ...currentDecision.uncertainty,
                score: uncertaintyScore,
              }
              : currentDecision.uncertainty
          }

        />


        <WhatIfPanel />


      </main>

    </div>
  );
}


export default App;