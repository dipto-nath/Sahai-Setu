import asyncio
from app.services.case_service import CaseService
from app.schemas.cases import CaseCreate
import traceback

async def main():
    try:
        svc = CaseService(use_demo=True)
        # Fake a DB connection by making sure we get_db
        case = svc.create_case(CaseCreate(language="en"))
        print(f"Created case {case['id']}")
        
        result = await svc.analyze_case(
            case_id=case['id'],
            text="They are trying to kill me, please send police now! I am scared.",
            language="en"
        )
        print("Analysis successful:", result)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
