# POST /heroes (Authenticated) - Create a new hero
# GET /heroes (Public) - Get list of all heroes
# GET /heroes/{hero_id} (Public) - Get hero by ID
# PATCH /heroes/{hero_id} (Authenticated) - Update part of hero by ID
# DELETE /heroes/{hero_id} (Admin only) - Delete hero by ID (can't delete hero with active missions)

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.models import Hero, Mission
from app.dependencies import SessionDependency, get_current_user, get_current_admin
from app.models.hero_schema import HeroCreateRequest, HeroUpdateRequest, HeroResponse

router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.post("/", status_code=201, response_model=HeroResponse)
def create_hero(request: HeroCreateRequest, session: SessionDependency, current_user=Depends(get_current_user)):
    """Create a new hero."""
    new_hero = Hero(
        name=request.name, 
        power=request.power
    )

    session.add(new_hero)
    session.commit()
    session.refresh(new_hero)

    return new_hero

@router.get("/", response_model=list[HeroResponse])
def get_heroes(session: SessionDependency):
    """Get list of all heroes."""
    return session.exec(select(Hero)).all()

@router.get("/{hero_id}", response_model=HeroResponse)
def get_hero(hero_id: int, session: SessionDependency):
    """Get a hero by ID."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    return hero

@router.patch("/{hero_id}", response_model=HeroResponse)
def update_hero(hero_id: int, request: HeroUpdateRequest, session: SessionDependency, current_user=Depends(get_current_user)):
    """Update a hero by ID."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    if request.name is not None:
        hero.name = request.name
    if request.power is not None:
        hero.power = request.power

    session.add(hero)
    session.commit()
    session.refresh(hero)

    return hero

@router.delete("/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDependency, current_user=Depends(get_current_admin)):
    """Delete a hero by ID."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    # Check for active missions (completed=False) for the hero
    active_mission = session.exec(select(Mission).where(Mission.hero_id == hero_id, Mission.completed == False)).first()
    if active_mission:
        raise HTTPException(status_code=400, detail="Cannot delete hero with active missions")
    
    session.delete(hero)
    session.commit()
    return
