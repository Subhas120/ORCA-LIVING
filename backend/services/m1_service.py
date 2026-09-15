"""M4 Service wrapping M1 Decision Intelligence Pipeline."""

import uuid
from orca_living.engines.decision_pipeline import DecisionIntelligencePipeline, DecisionPipelineInput
from orca_living.models.objective import UserObjective, TimeWindow, GeographicRegion, VesselContext

class M1Service:
    def __init__(self):
        self.pipeline = DecisionIntelligencePipeline()

    def run_decision_pipeline(self, world_state, proposals, safety_evaluations, request):
        from datetime import datetime, timedelta
        objective = UserObjective(
            original_query=request.query,
            operation=request.activity,
            primary_objective="opportunity",
            secondary_objectives=tuple(),
            time_window=TimeWindow(start=datetime.now(), end=datetime.now() + timedelta(hours=24)),
            region=GeographicRegion(name=request.location),
            vessel=VesselContext(category=request.vessel_type or "Unknown"),
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
