from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.models import Mission, Hero
from app.dependencies import SessionDependency, get_current_user, get_current_admin
from app.models.mission_schema import MissionCreateRequest, MissionUpdateRequest, MissionResponse

router = APIRouter(prefix="/missions", tags=["missions"])

@router.post("/", status_code=201, response_model=MissionResponse)
def create_mission(request: MissionCreateRequest, session: SessionDependency, current_user=Depends(get_current_user)):
    """Create a new mission for a hero."""
    hero = session.get(Hero, request.hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found.")
    if not hero.active:
        raise HTTPException(status_code=400, detail="Cannot assign mission to an inactive hero.")
    
    new_mission = Mission(
        title=request.title,
        difficulty=request.difficulty,
        hero_id=request.hero_id
    )

    session.add(new_mission)
    session.commit()
    session.refresh(new_mission)

    return new_mission

@router.get("/", response_model=list[MissionResponse])
def get_missions(session: SessionDependency):
    """Get list of all missions."""
    return session.exec(select(Mission)).all()

@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, session: SessionDependency):
    """Get mission by ID."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return mission

@router.patch("/{mission_id}", response_model=MissionResponse)
def update_mission(mission_id: int, request: MissionUpdateRequest, session: SessionDependency, current_user=Depends(get_current_user)):
    """Update a mission by ID."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    if request.title is not None:
        mission.title = request.title
    if request.difficulty is not None:
        mission.difficulty = request.difficulty
    if request.completed is not None:
        mission.completed = request.completed
    if request.hero_id is not None:
        hero = session.get(Hero, request.hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found.")
        mission.hero_id = request.hero_id

    session.add(mission)
    session.commit()
    session.refresh(mission)

    return mission

@router.delete("/{mission_id}", status_code=204)
def delete_mission(mission_id: int, session: SessionDependency, current_user=Depends(get_current_admin)):
    """Delete a mission by ID, only admin"""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    session.delete(mission)
    session.commit()
    return