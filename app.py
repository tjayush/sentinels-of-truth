from flask import Flask, render_template, request, jsonify
from database.db import create_tables, get_all_claims
from agents.orchestrator import AgentOrchestrator

app = Flask(__name__)

create_tables()
orchestrator = AgentOrchestrator()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/claims")
def claims_page():
    claims = get_all_claims()
    return render_template("claims.html", claims=claims)


@app.route("/verify", methods=["POST"])
def verify_claim():
    data = request.get_json() or {}
    claim = data.get("claim", "")

    final_state = orchestrator.route_claim_verification(claim)

    return jsonify({
        "claim": claim,
        "verification_report": final_state.get("verification_report", {}),
        "database_decision": final_state.get("database_decision", "UNKNOWN"),
        "history": final_state.get("history", [])
    })


if __name__ == "__main__":
    app.run(debug=True)