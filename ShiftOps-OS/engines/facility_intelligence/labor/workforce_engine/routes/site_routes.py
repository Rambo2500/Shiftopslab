from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from workforce_engine.database import get_db
from workforce_engine.models import Site, Line
from workforce_engine.schemas.site import SiteCreate, SiteResponse, LineCreate, LineResponse

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.post("/", response_model=SiteResponse)
def create_site(site: SiteCreate, db: Session = Depends(get_db)):
    db_site = Site(name=site.name)
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site


@router.get("/", response_model=list[SiteResponse])
def list_sites(db: Session = Depends(get_db)):
    return db.query(Site).all()


@router.post("/lines", response_model=LineResponse)
def create_line(line: LineCreate, db: Session = Depends(get_db)):
    db_line = Line(
        name=line.name,
        site_id=line.site_id,
        department=line.department,
        active=line.active
    )
    db.add(db_line)
    db.commit()
    db.refresh(db_line)
    return db_line


@router.get("/{site_id}/lines", response_model=list[LineResponse])
def list_lines(site_id: str, db: Session = Depends(get_db)):
    return db.query(Line).filter(Line.site_id == site_id).all()
