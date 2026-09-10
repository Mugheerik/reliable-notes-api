from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from reliable_notes_api.database import get_db
from reliable_notes_api.models import User, Note
from reliable_notes_api.schemas import NoteResponse, TokenResponse, UserRegister ,UserLogin ,NoteCreate , NoteUpdate, UserResponse
from reliable_notes_api.security import create_access_token, hash_password ,verify_password
from reliable_notes_api.auth import get_current_user
from uuid import UUID

app = FastAPI(title="Reliable Notes API")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Reliable Notes API!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/register")
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or username already exists",
        )

    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "message": "User registered successfully",
    }

@app.post("/auth/login", response_model=TokenResponse)
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(str(existing_user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.get("/users/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }

@app.post("/notes", response_model=NoteResponse)
def create_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_note = Note(
        title=note.title,
        content=note.content,
        owner_id=current_user.id,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note

@app.get("/notes", response_model=list[NoteResponse])
def list_notes(
    search: str | None = None,
    archived: bool = False,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Note)
        .filter(
            Note.owner_id == current_user.id,
            Note.archived == archived,
        )
    )

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Note.title.ilike(search_pattern))
            | (Note.content.ilike(search_pattern))
        )

    notes = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return notes

@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    return note


@app.patch("/notes/{note_id}")
def update_note(
    note_id: UUID,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    update_data = note_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)

    return note


@app.delete("/notes/{note_id}")
def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted successfully",
    }


@app.post("/notes/{note_id}/archive", response_model=NoteResponse)
def archive_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    note.archived = True
    db.commit()
    db.refresh(note)

    return note


@app.post("/notes/{note_id}/unarchive", response_model=NoteResponse)
def unarchive_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    note.archived = False
    db.commit()
    db.refresh(note)

    return note