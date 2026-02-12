# agents/impact_agent.py

def analyze_impact(files, target):
    return {
        "impacted_files": files,
        "reason": f"These files import or depend on {target}"
    }
