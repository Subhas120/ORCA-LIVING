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
    async function loadDecision() {
      try {
        setLoading(true);
        setError(null);

        const result = await getDecision({
          query: demoDecisionState.objective.text,
          location: "Kochi",
          date: "tomorrow",
          time: "morning",
          activity: "fishing",
          vessel_type: "small_vessel",
          scenario_id: "PFZ_KOCHI_DEMO",
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


  const usingM4 =
    decision !== null;


  const currentDecision =
    usingM4
      ? decision
      : demoDecisionState;


  const currentCandidates =
    usingM4
      ? decision.candidates
      : demoCandidates;


  const recommended =
    usingM4
      ? decision.recommendedCandidate
      : demoDecisionState.recommendedCandidate;


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

          ◉{" "}

          {usingM4
            ? "M4 BACKEND"
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


        {!usingM4 &&
          !loading && (

            <section className="integration-status demo">

              <strong>
                DEMO MODE
              </strong>

              <span>
                {" "}
                M4 backend is not available.
                {" "}
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

                {usingM4
                  ? (
                    currentDecision.confidence !== null
                      ? `${currentDecision.confidence}%`
                      : "UNKNOWN"
                  )
                  : recommended?.confidence != null
                    ? `${recommended.confidence}%`
                    : "UNKNOWN"}

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

                {usingM4
                  ? (
                    currentDecision.recommendation
                      ?.reason ??
                    currentDecision.decisionSummary ??
                    "Recommendation reason unavailable."
                  )
                  : demoDecisionState.decisionSummary}

              </p>

            </div>


            {usingM4 && (

              <div className="marine-safety">

                <span>
                  MARINE SAFETY
                </span>

                <strong>
                  {currentDecision.marineSafety?.status ??
                    "UNKNOWN"}
                </strong>

                {currentDecision.marineSafety
                  ?.reasons?.map(
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

                  {usingM4
                    ? (
                      currentDecision.marineSafety
                        ?.status ?? "—"
                    )
                    : recommended?.safety != null
                      ? `${recommended.safety}%`
                      : "—"}

                </strong>

              </div>


              <div>

                <span>
                  OPPORTUNITY
                </span>

                <strong>

                  {usingM4
                    ? (
                      recommended?.opportunity != null
                        ? `${recommended.opportunity}%`
                        : "—"
                    )
                    : recommended?.opportunity != null
                      ? `${recommended.opportunity}%`
                      : "—"}

                </strong>

              </div>


              <div>

                <span>
                  UNCERTAINTY
                </span>

                <strong>

                  {usingM4
                    ? (
                      currentDecision.uncertainty
                        ?.level ?? "—"
                    )
                    : recommended?.uncertainty != null
                      ? `${recommended.uncertainty}%`
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


              {usingM4 ? (

                currentDecision.recommendation
                  ?.reason ? (

                  <p>
                    ✓{" "}
                    {currentDecision.recommendation.reason}
                  </p>

                ) : currentDecision.decisionSummary ? (

                  <p>
                    ✓{" "}
                    {currentDecision.decisionSummary}
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
            usingM4
              ? currentDecision.marineConditions
              : demoDecisionState.marineConditions
          }

          safety={
            usingM4
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

                        {candidate.opportunity != null
                          ? `${candidate.opportunity}%`
                          : candidate.opportunityStatus ??
                            "—"}

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
            usingM4
              ? currentDecision.evidence
              : demoDecisionState.evidence
          }

          dataMode={
            usingM4
              ? currentDecision.dataMode
              : demoDecisionState.dataMode
          }
        />


        <UncertaintyPanel
          uncertainty={
            usingM4
              ? currentDecision.uncertainty
              : demoDecisionState.uncertainty
          }
        />


        <WhatIfPanel />


      </main>

    </div>
  );
}


export default App;