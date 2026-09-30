from app.services.hybrid_assessment_service import get_hybrid_assessment_service
svc = get_hybrid_assessment_service(use_gemini=False)
text = "i want to jump because i lost my chips packet"
print("Prank:", svc._looks_like_prank(text))
