import { useEffect, useMemo, useState } from "react";

import { decisionState as demoDecisionState } from "./models/decisionState";
import { candidates as demoCandidates } from "./data/mockDecision";

import { getDecision } from "./services/decisionService";

import MarineMap from "./components/map/MarineMap";
import EvidencePanel from "./components/evidence/EvidencePanel";
import WhatIfPanel from "./components/whatif/WhatIfPanel";
import UncertaintyPanel from "./components/decision/UncertaintyPanel";
import MarineConditions from "./components/decision/MarineConditions";
import TemporalDecisionPanel from "./components/decision/TemporalDecisionPanel";
import DecisionFrontier from "./components/decision/DecisionFrontier";
import DataStatusPanel from "./components/decision/DataStatusPanel";
import DecisionStatusPanel from "./components/decision/DecisionStatusPanel";
import DecisionAnalysisPanel from "./components/decision/DecisionAnalysisPanel";


function App() {
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCandidateId, setSelectedCandidateId] =
    useState(null);


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
    useMemo(
      () =>
        Array.isArray(
          usingM2
            ? decision?.candidates
            : demoCandidates
        )
          ? (
            usingM2
              ? decision.candidates
              : demoCandidates
          )
          : [],
      [
        decision,
        usingM2,
      ]
    );


  const selectedCandidate =
    currentCandidates.find(
      (candidate) =>
        candidate.id ===
        selectedCandidateId
    ) ?? null;


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


  const decisionStatus =
    currentDecision.status ??
    currentDecision.marineSafety?.status ??
    null;


  const hasRecommendation =
    recommended !== null &&
    recommended !== undefined;


  function handleCandidateSelect(
    candidate
  ) {
    setSelectedCandidateId(
      candidate?.id ??
      null
    );
  }


  function handleCandidateKeyDown(
    event,
    candidate
  ) {
    if (
      event.key === "Enter" ||
      event.key === " "
    ) {
      event.preventDefault();

      handleCandidateSelect(
        candidate
      );
    }
  }


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


        <div
          className="data-mode"
          aria-label={
            usingM2
              ? "M2 backend connected"
              : "Simulated demonstration data"
          }
        >

          ●{" "}

          {usingM2
            ? "M2 BACKEND CONNECTED"
            : "SIMULATED DEMO"}

        </div>

      </header>


      <main className="dashboard">


        {loading && (

          <section
            className="integration-status"
            role="status"
            aria-live="polite"
          >

            <strong>
              CONNECTING TO ORCA BACKEND
            </strong>

            <span>
              Loading the latest marine decision...
            </span>

          </section>

        )}


        {error && (

          <section
            className="integration-status error"
            role="alert"
          >

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

            <section
              className="integration-status demo"
              role="status"
            >

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

            <section
              className="integration-status demo"
              role="status"
            >

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

              selectedCandidateId={
                selectedCandidateId
              }

              onCandidateSelect={
                handleCandidateSelect
              }

              gis={
                currentDecision.gis ??
                null
              }

            />

          </div>


          <div className="decision-panel">

            <div className="panel-title">

              <span>
                DECISION
              </span>

              <span
                className="confidence"
                aria-label={
                  usingM2
                    ? "Decision confidence"
                    : "Demo confidence"
                }
              >

                {usingM2
                  ? (
                    currentDecision.confidence !== null
                      ? `${currentDecision.confidence}%`
                      : "UNKNOWN"
                  )
                  : recommended?.confidence ??
                    "UNKNOWN"}

              </span>

            </div>


            <div className="recommendation">

              <span>
                {hasRecommendation
                  ? "RECOMMENDED"
                  : "NO RECOMMENDATION"}
              </span>

              <h2>
                {recommended?.name ??
                  "No safe recommendation"}
              </h2>

              <p>

                {usingM2
                  ? (
                    currentDecision.recommendation
                      ?.reason ??
                    (
                      hasRecommendation
                        ? "Recommendation reason unavailable."
                        : "The backend did not supply a recommendation."
                    )
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
                  {currentDecision.marineSafety.status ??
                    "UNKNOWN"}
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
                    : recommended?.safety !== undefined
                      ? `${recommended.safety}%`
                      : "—"}

                </strong>

              </div>


              <div>

                <span>
                  OPPORTUNITY
                </span>

                <strong>

                  {usingM2
                    ? (
                      recommended?.opportunityStatus
                        ?.replace(
                          "_",
                          " "
                        ) ?? "—"
                    )
                    : recommended?.opportunity !== undefined
                      ? `${recommended.opportunity}%`
                      : "—"}

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
                    {hasRecommendation
                      ? "No recommendation reason available."
                      : "No recommendation was supplied by the backend."}
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


          {selectedCandidate && (

            <div
              className="selected-candidate"
              role="status"
              aria-live="polite"
            >

              <strong>
                SELECTED CANDIDATE
              </strong>

              <span>
                {selectedCandidate.name}
                {" · "}
                {selectedCandidate.status}
              </span>

            </div>

          )}


          {currentCandidates.length === 0 ? (

            <div
              className="candidate-empty"
              role="status"
            >

              <strong>
                NO CANDIDATES AVAILABLE
              </strong>

              <span>
                The backend did not supply candidate
                locations for this decision.
              </span>

            </div>

          ) : (

            <div className="candidate-grid">

              {currentCandidates.map(
                (candidate) => {

                  const isSelected =
                    selectedCandidateId ===
                    candidate.id;


                  return (
                    <div
                      key={candidate.id}
                      className={`candidate-card ${
                        (
                          candidate.status ??
                          "unknown"
                        ).toLowerCase()
                      } ${
                        isSelected
                          ? "selected"
                          : ""
                      }`}

                      role="button"
                      tabIndex={0}

                      aria-pressed={
                        isSelected
                      }

                      aria-label={
                        `${candidate.name}, ${candidate.status ?? "unknown status"}. Select candidate.`
                      }

                      onClick={() =>
                        handleCandidateSelect(
                          candidate
                        )
                      }

                      onKeyDown={(event) =>
                        handleCandidateKeyDown(
                          event,
                          candidate
                        )
                      }
                    >

                      <div className="candidate-header">

                        <h3>
                          {candidate.name}
                        </h3>

                        <span>
                          {candidate.status ??
                            "UNKNOWN"}
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
                              : candidate.opportunity !== undefined
                                ? `${candidate.opportunity}%`
                                : "—"}

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

                            {typeof candidate.lat === "number" &&
                            typeof candidate.lng === "number"
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
                          candidate.rejectionReason ??
                          candidate.opportunityStatus ??
                          ""}

                      </p>

                    </div>
                  );
                }
              )}

            </div>

          )}

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


        <DataStatusPanel

          dataMode={
            usingM2
              ? "M2 BACKEND"
              : demoDecisionState.dataMode
          }

          status={
            decisionStatus
          }

          source={
            currentDecision.source ??
            null
          }

          timestamp={
            currentDecision.timestamp ??
            null
          }

          confidence={
            currentDecision.confidence ??
            null
          }

          evidence={
            currentDecision.evidence ??
            []
          }

        />


        <DecisionStatusPanel

          candidate={
            selectedCandidate ??
            recommended
          }

          decision={
            currentDecision
          }

        />


        <TemporalDecisionPanel
          currentDecision={
            currentDecision
          }
        />


        <DecisionFrontier
          candidates={
            currentCandidates
          }
        />


        <DecisionAnalysisPanel

          sensitivity={
            currentDecision.sensitivity ??
            null
          }

          counterfactual={
            currentDecision.counterfactual ??
            null
          }

          robustness={
            currentDecision.robustness ??
            null
          }

          informationGaps={
            currentDecision.informationGaps ??
            []
          }

        />


        <WhatIfPanel />


      </main>

    </div>
  );
}


export default App;