def adapt_result(result, case_id):
    if not result.get("success"):
        return {
            "case_id": case_id,
            "svi": 0,
            "risk_level": "LOW",
            "confidence": 0.0,
            "assessment_status": "INCONCLUSIVE",
            "indicators": [],
            "recommendations": [],
            "explanation": {"error": result.get("error")},
            "analysis_mode": "REAL"
        }
    
    final = result.get("final_assessment", {})
    return {
        "case_id": case_id,
        "svi": final.get("svi", 0),
        "risk_level": final.get("risk_level", "LOW"),
        "confidence": final.get("confidence", 0) / 100.0,
        "assessment_status": final.get("assessment_status", "INCONCLUSIVE"),
        "indicators": result.get("indicators", []),
        "recommendations": result.get("recommendations", []),
        "explanation": result.get("processing_steps", []),
        "nlp_analysis": result.get("text_features", {}),
        "analysis_mode": "REAL"
    }
