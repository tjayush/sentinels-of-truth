from agents.investigator import InvestigatorAgent
from agents.archivist import ArchivistAgent

class AgentOrchestrator:
    def __init__(self, debug_mode: bool = True):
        self.investigator = InvestigatorAgent(debug_mode=debug_mode)
        self.archivist = ArchivistAgent(debug_mode=debug_mode)
        self.debug_mode = debug_mode

    def route_claim_verification(self, raw_claim: str) -> dict:
        state = {
            "claim": raw_claim,
            "history": ["[Orchestrator] Initializing multi-agent verification pipeline."],
            "verification_report": {},
            "db_similarity_context": {},
            "database_decision": "PENDING"
        }

        try:
            state["history"].append("[Orchestrator] Deploying Agent Alpha (Investigator) to collect data inputs.")
            investigation_results = self.investigator.execute_investigation(
                claim=state["claim"],
                history=state["history"]
            )
            
            state["verification_report"] = investigation_results.get("verification_report", {})
            state["db_similarity_context"] = investigation_results.get("db_similarity_context", {})

            report = state["verification_report"]
            if report.get("status") == "UNCERTAIN" and report.get("confidence", 0.0) == 0.0:
                state["history"].append("[Orchestrator] Pipeline execution halted prematurely by early agent abort guards.")
                state["database_decision"] = "ABORTED"
                return state

            state["history"].append("[Orchestrator] Deploying Agent Beta (Archivist) for knowledge asset validation.")
            state = self.archivist.process_report(state)
            state["history"].append(f"[Orchestrator] Pipeline successfully concluded. Final decision: {state['database_decision']}")

        except Exception as e:
            error_msg = f"[Orchestrator] Critical core engine processing exception -> {str(e)}"
            if self.debug_mode:
                print(error_msg)

            state["history"].append(error_msg)
            state["database_decision"] = "SYSTEM_ERROR"
            state["verification_report"] = {
                "status": "UNCERTAIN",
                "confidence": 0.0,
                "evidence": ["System runtime orchestration tracking pipeline exception occurred."]
            }

        return state