import sys
sys.path.append('backend')
try:
    from backend.app.services.analysis_service import AnalysisService
    print("Imported successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
