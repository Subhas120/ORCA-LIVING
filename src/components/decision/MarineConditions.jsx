function MarineConditions({
  conditions,
}) {
  const safety =
    conditions?.safety || {};

  const hasConditions =
    conditions &&
    (
      conditions.sst !== undefined ||
      conditions.chlorophyll !== undefined ||
      conditions.waveHeight !== undefined ||
      conditions.wavePeriod !== undefined ||
      conditions.currentSpeed !== undefined
    );


  return (
    <section className="marine-conditions">

      <div className="panel-title">

        <span>
          MARINE CONDITIONS
        </span>

        <span>
          {safety.status || "UNAVAILABLE"}
        </span>

      </div>


      {!hasConditions ? (

        <div className="conditions-unavailable">

          <strong>
            MARINE CONDITION DATA UNAVAILABLE
          </strong>

          <p>
            No marine-condition values have been
            supplied by the connected backend.
            No environmental values are being
            generated locally.
          </p>

          <span>
            DATA SOURCE: BACKEND REQUIRED
          </span>

        </div>

      ) : (

        <>

          <div className="conditions-grid">

            <div>
              <span>SST</span>

              <strong>
                {conditions.sst ?? "—"}
              </strong>
            </div>


            <div>
              <span>CHLOROPHYLL</span>

              <strong>
                {conditions.chlorophyll ?? "—"}
              </strong>
            </div>


            <div>
              <span>WAVE HEIGHT</span>

              <strong>
                {conditions.waveHeight !== null &&
                conditions.waveHeight !== undefined
                  ? `${conditions.waveHeight} m`
                  : "—"}
              </strong>
            </div>


            <div>
              <span>WAVE PERIOD</span>

              <strong>
                {conditions.wavePeriod !== null &&
                conditions.wavePeriod !== undefined
                  ? `${conditions.wavePeriod} s`
                  : "—"}
              </strong>
            </div>


            <div>
              <span>CURRENT</span>

              <strong>
                {conditions.currentSpeed !== null &&
                conditions.currentSpeed !== undefined
                  ? `${conditions.currentSpeed} m/s`
                  : "—"}
              </strong>
            </div>

          </div>


          {safety.reasons?.length > 0 && (

            <div className="safety-reasons">

              <strong>
                SAFETY REASONING
              </strong>

              {safety.reasons.map(
                (reason) => (

                  <p key={reason}>
                    • {reason}
                  </p>

                )
              )}

            </div>

          )}

        </>

      )}

    </section>
  );
}

export default MarineConditions;