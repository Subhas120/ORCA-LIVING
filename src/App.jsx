import { useEffect, useMemo, useState } from "react";

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

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState(null);

  const decisionRequest = {
    query: "Find a safe fishing location",
    location: "Kochi",
    date: "2026-09-15",
    time: "morning",
    activity: "fishing",
    vessel_type: "Small vessel",
  };


  const [selectedCandidateId, setSelectedCandidateId] =
    useState(null);


  useEffect(() => {
    const endpoint =
      import.meta.env.VITE_ORCA_DECISION_ENDPOINT;

    if (!endpoint) {
      return;
    }


    async function loadDecision() {
      try {
        setLoading(true);
        setError(null);
        const result = await getDecision(decisionRequest);

        setDecision(
          result
        );

      } catch (err) {
        console.error(
          err
        );

        setError(
          err?.message ??
          "Unable to load ORCA decision."
        );

      } finally {
        setLoading(
          false
        );
      }
    }


    loadDecision();

  }, []);


  const usingM4 =
    decision !== null;


  const currentDecision = decision;


  const currentCandidates = useMemo(
    () =>
      Array.isArray(decision?.candidates)
        ? decision.candidates
        : [],
    [decision]
  );


  const selectedCandidate =
    currentCandidates.find(
      (candidate) =>
        candidate.id ===
        selectedCandidateId
    ) ?? null;


  const recommended =
    decision?.recommendedCandidate ?? null;


  const uncertaintyScore =
    decision?.uncertainty?.score ?? null;


  const decisionStatus =
    currentDecision?.status ??
    null;


  const hasRecommendation =
    recommended !== null &&
    recommended !== undefined;


  const paretoPoints =
    currentDecision?.decisionIntelligence?.paretoPoints ??
    [];


  const dataMode =
    currentDecision?.dataMode ?? "UNKNOWN";


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
      event.key ===
        "Enter" ||
      event.key ===
        " "
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
            usingM4
              ? "Final M4 decision backend connected"
              : "Simulated demonstration data"
          }
        >

          {"●"}{" "}

          {usingM4
            ? "M4 DECISION BACKEND CONNECTED"
            : "M4 DECISION BACKEND NOT AVAILABLE"}

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
              CONNECTING TO ORCA DECISION BACKEND
            </strong>

            <span>
              Loading the latest M4 decision
              through the integration endpoint...
            </span>

          </section>

        )}


        {error && (

          <section
            className="integration-status error"
            role="alert"
          >

            <strong>
              M4 BACKEND UNAVAILABLE
            </strong>

            <span>
              {error}
            </span>

          </section>

        )}


        {!usingM4 &&
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
                The final M4 decision endpoint
                is not configured. The dashboard
                is displaying clearly labelled
                simulated demonstration data.
              </span>

            </section>

          )}


        <section className="objective">

          <span>
            USER OBJECTIVE
          </span>

          <h2>
            {decisionRequest.query}
          </h2>

          <p>
            Vessel:{" "}
            {decisionRequest.vessel_type}

            {" · "}

            {decisionRequest.time}
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
                currentDecision?.gis ??
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
                aria-label="Decision confidence"
              >

                {currentDecision?.confidence !== null &&
                currentDecision?.confidence !== undefined
                  ? `${currentDecision.confidence}%`
                  : "NOT SUPPLIED"}

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

                {currentDecision?.recommendation?.reason ??
                  currentDecision?.decisionSummary ??
                  (hasRecommendation
                    ? "Recommendation reason unavailable."
                    : "The backend did not supply a recommendation.")}

              </p>

            </div>


            {usingM4 &&
              currentDecision
                ?.marineSafety
                ?.status && (

              <div className="marine-safety">

                <span>
                  MARINE SAFETY
                </span>

                <strong>
                  {currentDecision
                    .marineSafety
                    .status}
                </strong>


                {currentDecision
                  .marineSafety
                  .reasons
                  ?.map(
                    (reason) => (

                      <p
                        key={reason}
                      >
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

                  {currentDecision?.marineSafety?.status ??
                    "NOT SUPPLIED"}

                </strong>

              </div>


              <div>

                <span>
                  OPPORTUNITY
                </span>

                <strong>

                  {recommended?.opportunity !== null &&
                  recommended?.opportunity !== undefined
                    ? `${recommended.opportunity}%`
                    : "NOT SUPPLIED"}

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
                    : "NOT SUPPLIED"}

                </strong>

              </div>


              <div>

                <span>
                  DISTANCE
                </span>

                <strong>

                  {recommended
                    ?.distance !== null &&
                  recommended
                    ?.distance !== undefined
                    ? `${recommended.distance} km`
                    : "NOT SUPPLIED"}

                </strong>

              </div>

            </div>


            <div className="why">

              <h3>
                WHY?
              </h3>
              {currentDecision?.decisionSummary ? (
                <p>
                  {"✓"}{" "}{currentDecision.decisionSummary}
                </p>
              ) : (
                <p>
                  {hasRecommendation
                    ? "No decision explanation was supplied by the backend."
                    : "No recommendation was supplied by the backend."}
                </p>
              )}

            </div>

          </div>

        </section>


        <MarineConditions

          conditions={
            currentDecision?.marineConditions ?? null
          }

          safety={
            usingM4
              ? currentDecision
                  ?.marineSafety
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
                The decision service did not
                supply candidate locations for
                this decision.
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

                      className={
                        `candidate-card ${
                          (
                            candidate.status ??
                            "unknown"
                          ).toLowerCase()
                        } ${
                          isSelected
                            ? "selected"
                            : ""
                        }`
                      }

                      role="button"

                      tabIndex={0}

                      aria-pressed={
                        isSelected
                      }

                      aria-label={
                        `${candidate.name}, ` +
                        `${candidate.status ?? "unknown status"}. ` +
                        `Select candidate.`
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
                              "NOT SUPPLIED"}

                            {candidate.distance !== null &&
                            candidate.distance !== undefined
                              ? " km"
                              : ""}
                          </strong>

                        </div>


                        <div>

                          <small>
                            Opportunity
                          </small>

                          <strong>

                            {candidate
                              .opportunity !== null &&
                            candidate
                              .opportunity !== undefined
                              ? `${candidate.opportunity}%`
                              : "NOT SUPPLIED"}

                          </strong>

                        </div>


                        <div>

                          <small>
                            Confidence
                          </small>

                          <strong>

                            {candidate
                              .confidence !== null &&
                            candidate
                              .confidence !== undefined
                              ? `${candidate.confidence}%`
                              : "NOT SUPPLIED"}

                          </strong>

                        </div>


                        <div>

                          <small>
                            Location
                          </small>

                          <strong>

                            {typeof candidate.lat ===
                              "number" &&
                            typeof candidate.lng ===
                              "number"
                              ? (
                                <>
                                  {candidate.lat.toFixed(2)}
                                  {"°, "}
                                  {candidate.lng.toFixed(2)}
                                  {"°"}
                                </>
                              )
                              : "NOT SUPPLIED"}

                          </strong>

                        </div>

                      </div>


                      <p className="candidate-reason">

                        {candidate.reason ??
                          candidate.rejectionReason ??
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

          candidate={
            recommended
          }

          evidence={currentDecision?.evidence ?? []}

          dataMode={
            dataMode
          }

        />


        <UncertaintyPanel

          uncertainty={currentDecision?.uncertainty ?? {}}

        />


        <DataStatusPanel

          dataMode={
            dataMode
          }

          status={
            decisionStatus
          }

          source={
            currentDecision
              ?.source ??
            null
          }

          timestamp={
            currentDecision
              ?.timestamp ??
            null
          }

          confidence={
            currentDecision
              ?.confidence ??
            null
          }

          evidence={
            currentDecision
              ?.evidence ??
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

          paretoPoints={
            paretoPoints
          }

          selectedCandidateId={
            selectedCandidateId
          }

          onCandidateSelect={
            handleCandidateSelect
          }

        />


        <DecisionAnalysisPanel

          sensitivity={
            currentDecision
              ?.sensitivity ??
            null
          }

          counterfactual={
            currentDecision
              ?.counterfactual ??
            null
          }

          robustness={
            currentDecision
              ?.robustness ??
            null
          }

          informationGaps={
            currentDecision
              ?.informationGaps ??
            []
          }

        />


        <WhatIfPanel />

      </main>

    </div>
  );
}


export default App;