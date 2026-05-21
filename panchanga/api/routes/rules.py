"""
Rules and traditions management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends

from panchanga.models.requests import RuleEvaluateRequest
from panchanga.models.responses import (
    RulesListResponse, TraditionsListResponse, 
    RuleEvaluationResponse, ErrorResponse
)
from panchanga.services.panchanga_service import PanchangaService
from panchanga.rules.traditions import DEFAULT_TRADITION
from api.dependencies import get_service

router = APIRouter()


@router.get(
    "",
    response_model=RulesListResponse,
    summary="List Available Rules",
    description="""
Get a list of all available tithi determination rules.

Rules are evaluated in priority order (lower number = higher priority).
Each rule can:
- Make a tithi decision
- Defer to the next rule
- Apply only under certain conditions

### Available Rules

| Rule | Priority | Description |
|------|----------|-------------|
| `purnima_amavasya` | 5 | Special handling for full/new moon |
| `sunrise_based` | 10 | Tithi at sunrise = day's tithi |
| `ksaya_handling` | 15 | Handle skipped tithis |
| `vriddhi_handling` | 16 | Handle extended tithis |
| `span_based` | 20 | Require minimum tithi span |
| `muhurta_based` | 25 | Based on muhurta periods |
"""
)
async def list_rules(
    service: PanchangaService = Depends(get_service)
):
    """
    List all available tithi determination rules.
    """
    rules = service.get_available_rules()
    
    return RulesListResponse(
        rules=[{
            'name': r['name'],
            'description': r['description'],
            'priority': r['priority'],
            'enabled_by_default': r.get('enabled', True),
            'parameters': r.get('parameters', {})
        } for r in rules]
    )


@router.get(
    "/traditions",
    response_model=TraditionsListResponse,
    summary="List Available Traditions",
    description="""
Get a list of all available calculation traditions.

### Traditions

| Tradition | Description |
|-----------|-------------|
| **surya** | Surya Siddhanta (ca. AD 1000) - Classical Indian astronomical constants |
| **drik** | Drik Ganita - Modern ephemeris-based calculations |
| **lunar** | Lunar calendar conventions (Amanta/Purnimanta month endings) |

Each tradition defines:
- Which astronomical constants to use
- Default rules for tithi determination
- Ayanamsa calculation method
"""
)
async def list_traditions(
    service: PanchangaService = Depends(get_service)
):
    """
    List all available calculation traditions.
    """
    traditions = service.get_available_traditions()
    
    return TraditionsListResponse(
        traditions=[{
            'name': t['name'],
            'display_name': t['display_name'],
            'description': t['description'],
            'default_rules': t.get('default_rules', [])
        } for t in traditions],
        default_tradition=DEFAULT_TRADITION
    )


@router.post(
    "/evaluate",
    response_model=RuleEvaluationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Evaluation error"}
    },
    summary="Evaluate Rules (Debug)",
    description="""
Evaluate tithi rules for a specific date and get detailed trace information.

This is useful for debugging and understanding how the rules engine
determines the tithi for a given day.

The response includes:
- List of rules that were evaluated
- Which rule made the final decision
- Step-by-step evaluation trace
- Any special conditions (ksaya, vriddhi)
"""
)
async def evaluate_rules(
    request: RuleEvaluateRequest,
    service: PanchangaService = Depends(get_service)
):
    """
    Evaluate rules for a specific date with detailed tracing.
    """
    try:
        # Apply request settings if provided
        if request.location:
            service.settings.loc_lat = request.location.latitude
            service.settings.loc_lon = request.location.longitude
        
        service.settings.tradition = request.tradition
        
        result = service.evaluate_rules(
            request.year,
            request.month,
            request.day
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")
