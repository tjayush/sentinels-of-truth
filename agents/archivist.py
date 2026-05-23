from database.db import insert_claim, insert_flagged_claim

class ArchivistAgent:
    def __init__(self, debug_mode: bool = True):
        self.agent_name = "Agent Beta (Archivist)"
        self.debug_mode = debug_mode

    def log_activity(self, message: str, history_list: list):
        formatted_log = f"[{self.agent_name}] {message}"
        if self.debug_mode:
            print(formatted_log)
        history_list.append(formatted_log)

    
    def process_report(self, state: dict) -> dict:
        logs = state["history"]
        report = state["verification_report"]
        claim = state.get("claim", "").strip()
        
        status = report.get("status", "UNCERTAIN")
        confidence = report.get("confidence", 0.0)
        
        evidence_list = report.get("evidence", [])
        if not isinstance(evidence_list, list):
            evidence_list = [str(evidence_list)]
        evidence = " | ".join(evidence_list)

        self.log_activity("Running knowledge base lookups and conflict scanning...", logs)

        similarity_ctx = state.get("db_similarity_context", {})
        similarity_score = similarity_ctx.get("score", 0.0)

        if similarity_ctx.get("match_found"):
            matched_record = similarity_ctx.get("matched_record", {})
            old_status = matched_record.get("status", "UNKNOWN").upper()
            db_claim = matched_record.get("claim", "")
            
            self.log_activity(f"Semantic match detected in memory indexes (Similarity Score: {similarity_score}).", logs)

            if (
                status in ["VERIFIED", "FAKE"] and
                old_status in ["VERIFIED", "FAKE"] and
                status != old_status
            ):
                record_id = matched_record.get("id", "Unknown")
                
                try:
                    insert_flagged_claim(claim, f"Contradicts existing record ID {record_id}: '{db_claim}' (New verdict: {status})")
                    self.log_activity("Conflict found with existing data asset. Flagged for manual audit loop.", logs)
                    state["database_decision"] = "FLAGGED"
                except Exception as e:
                    self.log_activity(f"Database insertion failure while flagging record -> {str(e)}", logs)
                    state["database_decision"] = "DATABASE_ERROR"
                    
                return state
                
            self.log_activity("Duplicate verification request detected. Discarding to avoid redundancy.", logs)
            state["database_decision"] = "DISCARD"
            return state

        if status in ["VERIFIED", "LIKELY TRUE"]:
            try:
                insert_claim(claim, status, confidence, evidence)
                self.log_activity("Integrity validation passed. Entry saved into Knowledge Base.", logs)
                state["database_decision"] = "INSERTED"
            except Exception as e:
                self.log_activity(f"Database write failure on claim insertion -> {str(e)}", logs)
                state["database_decision"] = "DATABASE_ERROR"
            
        elif status == "FAKE":
            try:
                insert_claim(claim, "FAKE", confidence, evidence)
                self.log_activity("Core threat warning. Fake data asset tagged and recorded into block database.", logs)
                state["database_decision"] = "REJECTED"
            except Exception as e:
                self.log_activity(f"Database write failure while recording blocked claim -> {str(e)}", logs)
                state["database_decision"] = "DATABASE_ERROR"
            
        else:
            self.log_activity("Claims parameters remain ambiguous. Holding in staging state.", logs)
            state["database_decision"] = "UNCERTAIN"

        return state