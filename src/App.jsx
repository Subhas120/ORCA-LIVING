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

const STATUS = {
  DECISION_AVAILABLE: "DECISION_AVAILABLE",
  NO_SAFE_CANDIDATES: "NO_SAFE_CANDIDATES",
  INSUFFICIENT_EVIDENCE: "INSUFFICIENT_EVIDENCE",
  SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
};

const SCENARIO_OPTIONS = [
  {
    value: "",
    label: "Backend default",
  },
  {
    value: "NORMAL",
    label: "NORMAL",
  },
  {
    value: "UNSAFE_WEATHER",
    label: "UNSAFE WEATHER",
  },
  {
    value: "INSUFFICIENT_EVIDENCE",
    label: "INSUFFICIENT EVIDENCE",
  },
];

const INITIAL_REQUEST = {
  query: "Find a safe fishing location",
  location: "Kochi",
  date: "2026-09-15",
  time: "morning",
  activity: "fishing",
  vessel_type: "Small vessel",
  scenario_id: "",
};

function getStatusPresentation(status) {
  switch (status) {
    case STATUS.DECISION_AVAILABLE:
      return {
        label: "DECISION AVAILABLE",
        description:
          "M4 produced an actionable decision and an authoritative recommendation.",
        className: "available",
      };

    case STATUS.NO_SAFE_CANDIDATES:
      return {
        label: "NO SAFE CANDIDATES",
        description:
          "M4 found no candidate that can be presented as a safe actionable option.",
        className: "unsafe",
      };

    case STATUS.INSUFFICIENT_EVIDENCE:
      return {
        label: "INSUFFICIENT EVIDENCE",
        description:
          "M4 cannot establish a safe actionable decision because required evidence is missing.",
        className: "insufficient",
      };

    case STATUS.SERVICE_UNAVAILABLE:
      return {
        label: "SERVICE UNAVAILABLE",
        description:
          "The decision service could not provide an authoritative decision.",
        className: "unavailable",
      };

    default:
      return {
        label: "DECISION STATUS UNKNOWN",
        description:
          "The backend returned an unrecognized decision state.",
        className: "unknown",
      };
  }
}

function App() {
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [selectedCandidateId, setSelectedCandidateId] = useState(null);
  const [request, setRequest] = useState(INITIAL_REQUEST);
  const [submittedRequest, setSubmittedRequest] = useState(INITIAL_REQUEST);

  const endpoint =
    import.meta.env.VITE_ORCA_DECISION_ENDPOINT;

  async function loadDecision(requestToSend) {
    if (!endpoint) {
      setBackendConnected(false);
      setDecision(null);
      setError(
        "ORCA M4 decision endpoint is not configured."
      );
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedCandidateId(null);

    try {
      const result = await getDecision(requestToSend);

      setDecision(result);
      setSubmittedRequest(requestToSend);
      setBackendConnected(true);
    } catch (err) {
      console.error(err);

      setBackendConnected(false);
      setDecision(null);
      setError(
        err?.message ??
          "Unable to load ORCA decision."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDecision(INITIAL_REQUEST);
  }, []);

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
        candidate.id === selectedCandidateId
    ) ?? null;

  const decisionStatus =
    currentDecision?.status ?? null;

  /*
   * Recommendation display is strictly controlled by
   * the authoritative M4 semantic status.
   *
   * M3 never creates a recommendation from the candidate
   * list or selects the first candidate as a fallback.
   */
  const recommended =
    decisionStatus === STATUS.DECISION_AVAILABLE
      ? currentDecision?.recommendedCandidate ?? null
      : null;

  const hasRecommendation =
    decisionStatus === STATUS.DECISION_AVAILABLE &&
    recommended !== null;

  const uncertaintyScore =
    currentDecision?.uncertainty?.score ?? null;

  const dataMode =
    currentDecision?.dataMode ?? "UNKNOWN";

  const statusPresentation =
    getStatusPresentation(decisionStatus);

  const paretoPoints =
    currentDecision?.decisionIntelligence
      ?.paretoPoints ?? [];

  function handleCandidateSelect(candidate) {
    setSelectedCandidateId(
      candidate?.id ?? null
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

      handleCandidateSelect(candidate);
    }
  }

  function handleRequestChange(event) {
    const { name, value } = event.target;

    setRequest((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function handleRequestSubmit(event) {
    event.preventDefault();

    const requiredFields = [
      "query",
      "location",
      "date",
      "time",
      "activity",
      "vessel_type",
    ];

    const missingField = requiredFields.find(
      (field) =>
        !String(request[field] ?? "").trim()
    );

    if (missingField) {
      setError(
        `Please provide the ${missingField.replace(
          "_",
          " "
        )}.`
      );
      return;
    }

    const requestToSend = {
      query: request.query.trim(),
      location: request.location.trim(),
      date: request.date,
      time: request.time.trim(),
      activity: request.activity.trim(),
      vessel_type: request.vessel_type.trim(),
    };

    if (request.scenario_id) {
      requestToSend.scenario_id =
        request.scenario_id;
    }

    loadDecision(requestToSend);
  }

  function handleRetry() {
    loadDecision(submittedRequest);
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>ORCA-LIVING</h1>

          <p>
            Marine Decision Intelligence
          </p>
        </div>

        <div
          className="data-mode"
          aria-label={
            backendConnected
              ? "Final M4 decision backend connected"
              : "Final M4 decision backend unavailable"
          }
        >
          {"●"}{" "}
          {backendConnected
            ? "M4 DECISION BACKEND CONNECTED"
            : "M4 DECISION BACKEND NOT AVAILABLE"}
        </div>
      </header>

      <main className="dashboard">
        <section className="request-panel">
          <div className="panel-title">
            <span>DECISION REQUEST</span>
            <span>
              M4 AUTHORITATIVE DECISION
            </span>
          </div>

          <form
            className="request-form"
            onSubmit={handleRequestSubmit}
            noValidate
          >
            <div className="request-field request-field-wide">
              <label htmlFor="query">
                Objective
              </label>

              <input
                id="query"
                name="query"
                type="text"
                value={request.query}
                onChange={handleRequestChange}
                placeholder="Describe the decision objective"
                required
              />
            </div>

            <div className="request-field">
              <label htmlFor="location">
                Location
              </label>

              <input
                id="location"
                name="location"
                type="text"
                value={request.location}
                onChange={handleRequestChange}
                placeholder="e.g. Kochi"
                required
              />
            </div>

            <div className="request-field">
              <label htmlFor="date">
                Date
              </label>

              <input
                id="date"
                name="date"
                type="date"
                value={request.date}
                onChange={handleRequestChange}
                required
              />
            </div>

            <div className="request-field">
              <label htmlFor="time">
                Time
              </label>

              <input
                id="time"
                name="time"
                type="text"
                value={request.time}
                onChange={handleRequestChange}
                placeholder="e.g. morning"
                required
              />
            </div>

            <div className="request-field">
              <label htmlFor="activity">
                Activity
              </label>

              <input
                id="activity"
                name="activity"
                type="text"
                value={request.activity}
                onChange={handleRequestChange}
                placeholder="e.g. fishing"
                required
              />
            </div>

            <div className="request-field">
              <label htmlFor="vessel_type">
                Vessel type
              </label>

              <input
                id="vessel_type"
                name="vessel_type"
                type="text"
                value={request.vessel_type}
                onChange={handleRequestChange}
                placeholder="e.g. Small vessel"
                required
              />
            </div>

            <div className="request-field">
              <label htmlFor="scenario_id">
                Controlled test scenario
              </label>

              <select
                id="scenario_id"
                name="scenario_id"
                value={request.scenario_id}
                onChange={handleRequestChange}
              >
                {SCENARIO_OPTIONS.map(
                  (option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  )
                )}
              </select>

              <small>
                Optional judge/demo control. The
                backend remains authoritative.
              </small>
            </div>

            <div className="request-actions">
              <button
                type="submit"
                className="request-submit"
                disabled={loading}
              >
                {loading
                  ? "REQUESTING DECISION..."
                  : "REQUEST DECISION"}
              </button>
            </div>
          </form>
        </section>

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

        {error && !loading && (
          <section
            className="integration-status error"
            role="alert"
          >
            <strong>
              M4 BACKEND UNAVAILABLE
            </strong>

            <span>{error}</span>

            <button
              type="button"
              className="retry-button"
              onClick={handleRetry}
              disabled={loading}
            >
              RETRY
            </button>
          </section>
        )}

        {currentDecision && (
          <section
            className={`decision-state ${statusPresentation.className}`}
            role="status"
            aria-live="polite"
            aria-label={`Decision status: ${statusPresentation.label}`}
          >
            <div>
              <strong>
                {statusPresentation.label}
              </strong>

              <span>
                {statusPresentation.description}
              </span>
            </div>

            <span className="decision-state-code">
              {decisionStatus}
            </span>
          </section>
        )}

        {currentDecision && (
          <section className="objective">
            <span>USER OBJECTIVE</span>

            <h2>
              {submittedRequest.query}
            </h2>

            <p>
              Location:{" "}
              {submittedRequest.location}
              {" · "}
              Vessel:{" "}
              {submittedRequest.vessel_type}
              {" · "}
              {submittedRequest.time}
            </p>
          </section>
        )}

        <section className="content-grid">
          <div className="map-panel">
            <div className="panel-title">
              <span>MARINE MAP</span>

              <span>
                {currentCandidates.length}{" "}
                CANDIDATES
              </span>
            </div>

            <MarineMap
              candidates={currentCandidates}
              selectedCandidateId={
                selectedCandidateId
              }
              onCandidateSelect={
                handleCandidateSelect
              }
              gis={
                currentDecision?.gis ?? null
              }
            />
          </div>

          <div className="decision-panel">
            <div className="panel-title">
              <span>DECISION</span>

              <span
                className="confidence"
                aria-label="Decision confidence"
              >
                {currentDecision?.confidence !==
                  null &&
                currentDecision?.confidence !==
                  undefined
                  ? `${currentDecision.confidence}%`
                  : "NOT SUPPLIED"}
              </span>
            </div>

            <div className="recommendation">
              <span>
                {hasRecommendation
                  ? "RECOMMENDED"
                  : statusPresentation.label}
              </span>

              <h2>
                {hasRecommendation
                  ? recommended.name
                  : "No actionable recommendation"}
              </h2>

              <p>
                {currentDecision?.recommendation
                  ?.reason ??
                  currentDecision?.decisionSummary ??
                  statusPresentation.description}
              </p>
            </div>

            {currentDecision?.marineSafety?.status && (
              <div className="marine-safety">
                <span>MARINE SAFETY</span>

                <strong>
                  {currentDecision.marineSafety.status}
                </strong>

                {currentDecision.marineSafety.reasons?.map(
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
                <span>SAFETY</span>

                <strong>
                  {currentDecision?.marineSafety
                    ?.status ??
                    "NOT SUPPLIED"}
                </strong>
              </div>

              <div>
                <span>OPPORTUNITY</span>

                <strong>
                  {hasRecommendation &&
                  recommended?.opportunity !==
                    null &&
                  recommended?.opportunity !==
                    undefined
                    ? `${recommended.opportunity}%`
                    : "NOT SUPPLIED"}
                </strong>
              </div>

              <div>
                <span>UNCERTAINTY</span>

                <strong>
                  {uncertaintyScore !== null &&
                  uncertaintyScore !== undefined
                    ? `${uncertaintyScore}%`
                    : "NOT SUPPLIED"}
                </strong>
              </div>

              <div>
                <span>DISTANCE</span>

                <strong>
                  {hasRecommendation &&
                  recommended?.distance !==
                    null &&
                  recommended?.distance !==
                    undefined
                    ? `${recommended.distance} km`
                    : "NOT SUPPLIED"}
                </strong>
              </div>
            </div>

            <div className="why">
              <h3>WHY?</h3>

              <p>
                {"✓"}{" "}
                {currentDecision?.decisionSummary ??
                  statusPresentation.description}
              </p>
            </div>
          </div>
        </section>

        <MarineConditions
          conditions={
            currentDecision?.marineConditions ??
            null
          }
          safety={
            currentDecision?.marineSafety ?? null
          }
        />

        <section className="candidates">
          <div className="section-heading">
            <h2>Candidates</h2>

            <span>PFZ LOCATIONS</span>
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
                M4 did not supply candidate
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
                      aria-pressed={isSelected}
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
                            {candidate.distance !==
                              null &&
                            candidate.distance !==
                              undefined
                              ? " km"
                              : ""}
                          </strong>
                        </div>

                        <div>
                          <small>
                            Opportunity
                          </small>

                          <strong>
                            {candidate.opportunity !==
                              null &&
                            candidate.opportunity !==
                              undefined
                              ? `${candidate.opportunity}%`
                              : "NOT SUPPLIED"}
                          </strong>
                        </div>

                        <div>
                          <small>
                            Confidence
                          </small>

                          <strong>
                            {candidate.confidence !==
                              null &&
                            candidate.confidence !==
                              undefined
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
                                  {candidate.lat.toFixed(
                                    2
                                  )}
                                  {"°, "}
                                  {candidate.lng.toFixed(
                                    2
                                  )}
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
          candidate={recommended}
          evidence={
            currentDecision?.evidence ?? []
          }
          dataMode={dataMode}
        />

        <UncertaintyPanel
          uncertainty={
            currentDecision?.uncertainty ?? {}
          }
        />

        <DataStatusPanel
          dataMode={dataMode}
          status={decisionStatus}
          source={
            currentDecision?.source ?? null
          }
          timestamp={
            currentDecision?.timestamp ?? null
          }
          confidence={
            currentDecision?.confidence ?? null
          }
          evidence={
            currentDecision?.evidence ?? []
          }
        />

        <DecisionStatusPanel
          candidate={
            selectedCandidate ?? recommended
          }
          decision={currentDecision}
        />

        <TemporalDecisionPanel
          currentDecision={currentDecision}
        />

        <DecisionFrontier
          candidates={currentCandidates}
          paretoPoints={paretoPoints}
          selectedCandidateId={
            selectedCandidateId
          }
          onCandidateSelect={
            handleCandidateSelect
          }
        />

        <DecisionAnalysisPanel
          sensitivity={
            currentDecision?.sensitivity ?? null
          }
          counterfactual={
            currentDecision?.counterfactuals ??
            null
          }
          robustness={
            currentDecision?.robustness ?? null
          }
          informationGaps={
            currentDecision?.informationGaps ?? []
          }
        />

        <WhatIfPanel />
      </main>
    </div>
  );
}

export default App;