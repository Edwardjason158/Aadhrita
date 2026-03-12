from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/nlp", tags=["NLP"])

class JournalRequest(BaseModel):
    text: str

@router.post("/analyze")
async def analyze_journal(request: JournalRequest):
    if not request.text or len(request.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please enter at least a few words to analyze.")
    if len(request.text) > 2000:
        raise HTTPException(status_code=400, detail="Text too long. Max 2000 characters.")
    
    try:
        from backend.services.indic_nlp_service import analyze_indic_health_text
        result = analyze_indic_health_text(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multilingual NLP analysis failed: {str(e)}")
