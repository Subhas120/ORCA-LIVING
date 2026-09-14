import {
  MapPin,
  ShieldCheck,
  Fish,
  Navigation,
  Info,
  AlertTriangle,
} from "lucide-react";

function FishermanMode({
  recommended,
  alternatives = [],
  rejected = [],
  decisionSummary,
  uncertainty,
}) {
  if (!recommended) {
    return (
      <section className="fisherman-mode">
        <div className="fisherman-empty">
          <AlertTriangle size={28} />

          <div>
            <h2>No recommendation available</h2>

            <p>
              ORCA does not currently have enough information
              to recommend a fishing location.
            </p>
          </div>
        </div>
      </section>
    );
  }

  const confidence =
    recommended.confidence ??
    uncertainty?.level ??
    "UNKNOWN";

  const confidenceText =
    typeof confidence === "number"
      ? `${confidence}% confidence`
      : confidence;

  return (
    <section className="fisherman-mode">

      {/* HEADER */}

      <div className="fisherman-header">

        <div>
          <span className="fisherman-label">
            FISHERMAN MODE
          </span>

          <h1>
            Your recommended fishing location
          </h1>

          <p>
            A simple view of ORCA's current decision.
          </p>
        </div>

        <div className="fisherman-confidence">
          <ShieldCheck size={20} />

          <span>
            {confidenceText}
          </span>
        </div>

      </div>


      {/* MAIN RECOMMENDATION */}

      <div className="fisherman-recommendation">

        <div className="go-badge">
          GO
        </div>

        <div className="recommendation-icon">
          <MapPin size={42} />
        </div>

        <div className="recommendation-main">

          <span className="recommendation-label">
            RECOMMENDED LOCATION
          </span>

          <h2>
            {recommended.name}
          </h2>

          <div className="recommendation-distance">
            <Navigation size={17} />

            <span>
              {recommended.distance != null
                ? `${recommended.distance} km away`
                : "Distance unavailable"}
            </span>
          </div>

        </div>

      </div>


      {/* SIMPLE REASONS */}

      <div className="fisherman-reasons">

        <div className="fisherman-reason">

          <ShieldCheck size={24} />

          <div>
            <span>SAFETY</span>

            <strong>
              Good conditions
            </strong>
          </div>

        </div>


        <div className="fisherman-reason">

          <Fish size={24} />

          <div>
            <span>FISHING OPPORTUNITY</span>

            <strong>
              {recommended.opportunityScore != null
                ? `${recommended.opportunityScore}%`
                : recommended.opportunity != null
                  ? `${recommended.opportunity}%`
                  : "Favorable"}
            </strong>
          </div>

        </div>


        <div className="fisherman-reason">

          <MapPin size={24} />

          <div>
            <span>DISTANCE</span>

            <strong>
              {recommended.distance != null
                ? `${recommended.distance} km`
                : "Unknown"}
            </strong>
          </div>

        </div>

      </div>


      {/* WHY */}

      <div className="fisherman-why">

        <div className="fisherman-why-title">

          <Info size={20} />

          <h3>
            Why this location?
          </h3>

        </div>

        <p>
          {decisionSummary ||
            "ORCA selected this location based on the available environmental and safety information."}
        </p>

      </div>


      {/* ALTERNATIVES */}

      {alternatives.length > 0 && (

        <div className="fisherman-options">

          <div className="fisherman-options-title">
            <span>
              OTHER OPTIONS
            </span>

            <small>
              If your situation changes
            </small>
          </div>

          <div className="fisherman-option-list">

            {alternatives.map((candidate) => (

              <div
                className="fisherman-option"
                key={candidate.id}
              >

                <div>
                  <strong>
                    CONSIDER
                  </strong>

                  <h3>
                    {candidate.name}
                  </h3>
                </div>

                <div className="option-distance">

                  {candidate.distance != null
                    ? `${candidate.distance} km`
                    : "Distance unknown"}

                </div>

              </div>

            ))}

          </div>

        </div>

      )}


      {/* SAFETY NOTICE */}

      {rejected.length > 0 && (

        <div className="fisherman-avoid">

          <AlertTriangle size={21} />

          <div>

            <strong>
              AVOID UNSAFE LOCATIONS
            </strong>

            <p>
              ORCA has identified {rejected.length} location
              {rejected.length > 1 ? "s" : ""} that should not
              be preferred under the current conditions.
            </p>

          </div>

        </div>

      )}

    </section>
  );
}

export default FishermanMode;