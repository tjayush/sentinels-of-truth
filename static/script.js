function generateConfidenceBar(score) {
    
    const normalized = Math.min(Math.max(parseFloat(score) || 0, 0), 1);
    const percentage = Math.round(normalized * 100);
    
    const filledBlocksCount = Math.round(percentage / 10);
    const emptyBlocksCount = 10 - filledBlocksCount;
    
    const filledBlocks = "█".repeat(filledBlocksCount);
    const emptyBlocks = "░".repeat(emptyBlocksCount);
    
    return `${filledBlocks}${emptyBlocks} ${percentage}%`;
}

async function verifyClaim() {
    const claim = document.getElementById("claimInput").value;

    if (claim.trim() === "") {
        alert("Please enter a claim");
        return;
    }

    document.getElementById("result-card").classList.remove("hidden");
    document.getElementById("logs-card").classList.add("hidden");

    document.getElementById("result-card").innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px; text-align: center;">
            <div class="agent-spinner" style="
                width: 45px; 
                height: 45px; 
                border: 4px solid #f3f3f3; 
                border-top: 4px solid #1d72b8; 
                border-radius: 50%; 
                animation: spin 1s linear infinite;
                margin-bottom: 20px;
            "></div>
            <h2 style="margin: 0 0 10px 0; color: #222;">Synchronizing Multi-Agent System...</h2>
            <p style="color: #666; font-size: 14px; margin: 0;">Deploying Agent Alpha to gather live evidence sweeps. Please wait.</p>
        </div>

        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;

    try {
        const response = await fetch("/verify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                claim: claim
            })
        });

        const data = await response.json();
        const report = data.verification_report || {};

        const status = report.status || "UNKNOWN";
        const confidenceBarText = generateConfidenceBar(report.confidence ?? 0);
        
        let evidenceText = "No clear evidence cataloged.";
        if (report.evidence) {
            evidenceText = Array.isArray(report.evidence) ? report.evidence.join(" | ") : String(report.evidence);
        }

        document.getElementById("result-card").innerHTML = `
            <h2>Verification Result</h2>

            <div class="result-item">
                <strong>Claim:</strong>
                ${data.claim || ""}
            </div>

            <div class="result-item">
                <strong>Status:</strong>
                ${status}
            </div>

            <div class="result-item">
                <strong>Confidence:</strong>
                <span style="font-family: monospace; font-weight: bold; color: #1d72b8;">${confidenceBarText}</span>
            </div>

            <div class="result-item">
                <strong>Evidence:</strong>
                ${evidenceText}
            </div>

            <div class="result-item">
                <strong>Database Decision:</strong>
                ${data.database_decision || "UNKNOWN"}
            </div>
        `;

        document.getElementById("logsList").innerHTML = "";
        document.getElementById("logs-card").classList.remove("hidden");

        (data.history || []).forEach(log => {
            const li = document.createElement("li");
            li.innerText = log;
            document.getElementById("logsList").appendChild(li);
        });

    } catch (error) {
        document.getElementById("result-card").innerHTML = `
            <h2>Error</h2>
            <p>Unable to verify claim. Please try again.</p>
        `;
        console.error(error);
    }
}