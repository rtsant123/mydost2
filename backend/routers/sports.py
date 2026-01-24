"""Sports predictions API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from services.sports_service import sports_service
from services.teer_service import teer_service
from models.sports_data import sports_db

router = APIRouter()


# ============= PYDANTIC MODELS =============

class MatchPredictionRequest(BaseModel):
    """Request for match prediction."""
    user_id: str
    team_1: str
    team_2: str


class MatchPredictionResponse(BaseModel):
    """Response for match prediction."""
    user_id: str
    teams: str
    prediction: str
    confidence: float
    user_history: dict
    timestamp: str


class TeerPredictionRequest(BaseModel):
    """Request for teer prediction."""
    user_id: str
    target_date: str
    predicted_first: str
    predicted_second: str
    reasoning: Optional[str] = ""


class UserSportsProfileRequest(BaseModel):
    """Request for user sports profile."""
    user_id: str


# ============= MATCH ENDPOINTS =============

@router.get("/sports/upcoming-matches")
async def get_upcoming_matches():
    """Get all upcoming matches from database."""
    try:
        data = sports_service.get_upcoming_matches_with_context()
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sports/predict-match")
async def predict_match(request: MatchPredictionRequest):
    """Predict match outcome with user memory consideration."""
    try:
        prediction = sports_service.predict_match_with_user_memory(
            user_id=request.user_id,
            team_1=request.team_1,
            team_2=request.team_2
        )
        
        return {
            "success": True,
            "prediction": prediction,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sports/save-prediction")
async def save_prediction(request: MatchPredictionRequest):
    """Save user's match prediction to database."""
    try:
        # Get upcoming matches for the teams
        matches = sports_db.get_upcoming_matches(days_ahead=7)
        
        # Find matching teams
        relevant_matches = [
            m for m in matches
            if (request.team_1.lower() in m.get("team_1", "").lower() or 
                request.team_1.lower() in m.get("team_2", "").lower()) and
               (request.team_2.lower() in m.get("team_1", "").lower() or 
                request.team_2.lower() in m.get("team_2", "").lower())
        ]
        
        if not relevant_matches:
            raise HTTPException(status_code=404, detail="No upcoming matches found for these teams")
        
        match_id = relevant_matches[0]["match_id"]
        prediction_text = f"Prediction for {request.team_1} vs {request.team_2}"
        
        pred_id = sports_service.save_match_prediction(
            user_id=request.user_id,
            match_id=match_id,
            prediction_text=prediction_text
        )
        
        return {
            "success": True,
            "prediction_id": pred_id,
            "message": "Prediction saved successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sports/profile/{user_id}")
async def get_sports_profile(user_id: str):
    """Get user's sports prediction profile and history."""
    try:
        profile = sports_service.get_user_sports_profile(user_id)
        return {
            "success": True,
            "profile": profile,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= TEER ENDPOINTS =============

@router.get("/teer/results")
async def get_teer_results():
    """Get teer results with pattern analysis."""
    try:
        data = teer_service.get_teer_with_pattern_analysis()
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/teer/predict")
async def predict_teer(request: TeerPredictionRequest):
    """Save user's teer prediction."""
    try:
        pred_id = teer_service.save_teer_prediction(
            user_id=request.user_id,
            target_date=request.target_date,
            predicted_first=request.predicted_first,
            predicted_second=request.predicted_second,
            reasoning=request.reasoning
        )
        
        return {
            "success": True,
            "prediction_id": pred_id,
            "message": "Teer prediction saved successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teer/accuracy/{user_id}")
async def get_teer_accuracy(user_id: str):
    """Get user's teer prediction accuracy."""
    try:
        accuracy = teer_service.get_teer_prediction_accuracy(user_id)
        return {
            "success": True,
            "accuracy": accuracy,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= COMBINED PROFILE ENDPOINT =============

@router.get("/profile/sports/{user_id}")
async def get_full_sports_profile(user_id: str):
    """Get complete sports profile including matches and teer."""
    try:
        match_profile = sports_service.get_user_sports_profile(user_id)
        teer_accuracy = teer_service.get_teer_prediction_accuracy(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "match_predictions": match_profile.get("match_predictions", {}),
            "teer_predictions": match_profile.get("teer_predictions", {}),
            "teer_accuracy": teer_accuracy,
            "overall_profile_created": match_profile.get("profile_created"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
