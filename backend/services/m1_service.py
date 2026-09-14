"""M4 Service wrapping M1 Decision Intelligence Pipeline."""

import uuid
from orca_living.engines.decision_pipeline import DecisionIntelligencePipeline, DecisionPipelineInput
from orca_living.models.objective import UserObjective, TimeWindow, GeographicRegion, VesselContext

class M1Service:
    def __init__(self):
        self.pipeline = DecisionIntelligencePipeline()

    def run_decision_pipeline(self, world_state, proposals, safety_evaluations, request):
        objective = UserObjective(
            id=str(uuid.uuid4()),
            original_query=request.query,
            operation=request.activity,
            primary_objective="Find safe opportunity",
            secondary_objectives=tuple(),
            time_window=TimeWindow(description=f"{request.date} {request.time}", start_time=None, end_time=None),
            region=GeographicRegion(description=request.location, center_lat=0.0, center_lng=0.0, radius_km=0.0),
            vessel=VesselContext(vessel_type=request.vessel_type or "Unknown", capabilities=tuple(), constraints=tuple()),
            constraints=tuple(),
            preferences=tuple()
        )
        
        pipeline_input = DecisionPipelineInput(
            world_state=world_state,
            proposals=proposals,
            safety_evaluations=safety_evaluations,
            objective=objective,
            decision_id=str(uuid.uuid4())
        )
        
        return self.pipeline.run(pipeline_input)
