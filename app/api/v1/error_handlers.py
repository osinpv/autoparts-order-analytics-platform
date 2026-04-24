from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def handle_integrity_error(db: Session, exc: IntegrityError) -> None:
    db.rollback()

    error_text = str(exc.orig).lower()
    print("DEBUG exc.orig:", repr(str(exc.orig)))
    print("DEBUG full exc:", repr(str(exc)))
    print("DEBUG error_text:", repr(error_text))

    if (
        "unique constraint" in error_text
        or "duplicate key value" in error_text
        or "already exists" in error_text
    ):
        raise HTTPException(
            status_code=409,
            detail="Record already exists.",
        )

    if (
        "foreign key constraint" in error_text
        or "violates foreign key constraint" in error_text
        or "is not present in table" in error_text
    ):
        raise HTTPException(
            status_code=400,
            detail="Referenced record does not exist.",
        )

    if (
        "not-null constraint" in error_text
        or "null value in column" in error_text
    ):
        raise HTTPException(
            status_code=400,
            detail="Required field is missing.",
        )

    raise HTTPException(
        status_code=400,
        detail=f"Database constraint error: {str(exc.orig)}",
    )