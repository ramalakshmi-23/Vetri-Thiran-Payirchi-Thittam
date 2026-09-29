import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .gemini_client import GeminiConfigurationError
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import User
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

templates = Jinja2Templates(directory="templates")
router = APIRouter()


def plan_to_json(plan) -> str:
    return plan.model_dump_json(indent=2)


def plan_to_display(plan) -> str:
    return json.dumps(plan.model_dump(), indent=2)


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error": None},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user_input = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        existing = db.scalar(select(User).where(User.user_id == user_input.user_id))
        if existing:
            raise ValueError(
                "That User ID already exists. Use a different User ID or update the existing plan."
            )

        workout = generate_workout_gemini(user_input)
        tip = generate_nutrition_tip_with_flash(user_input.goal, user_input.age)

        user = User(
            user_id=user_input.user_id,
            username=user_input.username,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
            original_plan=plan_to_json(workout),
            nutrition_tip=tip.tip,
        )
        db.add(user)
        db.commit()

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": plan_to_display(workout),
                "nutrition_tip": tip.tip,
                "recovery_note": tip.recovery_note,
                "message": None,
                "error": None,
            },
        )

    except GeminiConfigurationError as exc:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500,
        )
    except Exception as exc:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=400,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        request_data = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = db.scalar(select(User).where(User.user_id == request_data.user_id))

        if not user:
            raise ValueError("User ID was not found.")

        user_input = UserInput(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )

        updated = update_workout_plan(
            user_input,
            user.original_plan,
            request_data.feedback,
        )
        tip = generate_nutrition_tip_with_flash(user.goal, user.age)

        user.updated_plan = plan_to_json(updated)
        user.feedback = request_data.feedback
        user.nutrition_tip = tip.tip
        db.commit()

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "workout_plan": plan_to_display(updated),
                "nutrition_tip": tip.tip,
                "recovery_note": tip.recovery_note,
                "message": "Your plan was updated using your feedback.",
                "error": None,
            },
        )

    except GeminiConfigurationError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users},
    )


@router.get("/api/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}


@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "has_updated_plan": bool(u.updated_plan),
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.get("/api/users/{user_id}")
def api_user(user_id: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "user_id": user.user_id,
        "username": user.username,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "original_plan": json.loads(user.original_plan),
        "updated_plan": json.loads(user.updated_plan) if user.updated_plan else None,
        "nutrition_tip": user.nutrition_tip,
        "feedback": user.feedback,
    }
