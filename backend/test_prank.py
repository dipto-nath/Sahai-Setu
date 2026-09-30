from app.services.hybrid_assessment_service import get_hybrid_assessment_service
svc = get_hybrid_assessment_service(use_gemini=False)
print("Prank:", svc._looks_like_prank("this is a prank"))
print("Prank:", svc._looks_like_prank("stolen my chips"))
