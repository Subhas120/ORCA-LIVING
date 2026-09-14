function EvidencePanel({ candidate }) {
  const evidence = [
    {
      id: "E1",
      category: "Safety",
      observation: "Wave height = 1.6 m",
      source: "Ocean forecast",
      timestamp: "2026-09-11 06:00",
    },
    {
      id: "E2",
      category: "Opportunity",
      observation: "Favorable chlorophyll conditions",
      source: "Satellite observation",
      timestamp: "2026-09-11 05:30",
    },
  ];

  return (
    <section className="evidence-panel">

      {/* HEADER */}

      <div className="panel-title">
        <span>EVIDENCE</span>
        <span>DECISION SUPPORT</span>
      </div>


      {/* SUMMARY */}

      <div className="evidence-summary">

        <div>
          <h2>Why this location?</h2>

          <p>
            The recommendation is supported by the
            environmental evidence available to the
            decision system.
          </p>
        </div>

      </div>


      {/* EVIDENCE ITEMS */}

      <div className="evidence-list">

        {evidence.map((item) => (

          <div
            className="evidence-item"
            key={item.id}
          >

            <div className="evidence-main">

              <div className="evidence-category">
                {item.category}
              </div>

              <strong>
                {item.observation}
              </strong>

              <span>
                Source: {item.source}
              </span>

              <span>
                Observed: {item.timestamp}
              </span>

            </div>

            <div className="evidence-id">
              {item.id}
            </div>

          </div>

        ))}

      </div>


      {/* DECISION SIGNALS */}

      <div className="evidence-signals">

        <div>
          <span>SAFETY</span>

          <strong>
            {candidate.safety}%
          </strong>
        </div>

        <div>
          <span>OPPORTUNITY</span>

          <strong>
            {candidate.opportunity}%
          </strong>
        </div>

        <div>
          <span>UNCERTAINTY</span>

          <strong>
            {candidate.uncertainty}%
          </strong>
        </div>

        <div>
          <span>DISTANCE</span>

          <strong>
            {candidate.distance} km
          </strong>
        </div>

      </div>


      {/* DATA STATUS */}

      <div className="evidence-footer">

        <div>
          <span>DATA MODE</span>

          <strong>
            SIMULATED
          </strong>
        </div>

        <div>
          <span>PROVENANCE</span>

          <strong>
            SOURCE + TIMESTAMP
          </strong>
        </div>

      </div>

    </section>
  );
}

export default EvidencePanel;