import sys
sys.path.append('backend')
try:
    from app.services.analysis_service import AnalysisService
    svc = AnalysisService()
    print("Imported successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
