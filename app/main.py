from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from transformers import pipeline
from transformers.pipelines.base import Pipeline

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("moodplay")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

HF_MODEL = os.getenv(
    "HF_MODEL",
    "j-hartmann/emotion-english-distilroberta-base",
)

APP_NAME = os.getenv("APP_NAME", "MoodPlay")

# Use -1 for CPU. Set this to 0 only when the deployment has a supported GPU.
MODEL_DEVICE = int(os.getenv("MODEL_DEVICE", "-1"))

classifier: Pipeline | None = None


class MoodRequest(BaseModel):
    text: str = Field(
        min_length=2,
        max_length=1000,
        description="Text describing how the user currently feels.",
    )


GAME_PROFILES: dict[str, dict[str, Any]] = {
    "joy": {
        "game": "catch-stars",
        "title": "Catch the Stars",
        "message": "A bright, energetic challenge matched to upbeat cues.",
        "speed": 1.25,
        "difficulty": 0.6,
        "duration": 60,
    },
    "sadness": {
        "game": "gentle-garden",
        "title": "Gentle Garden",
        "message": "A quiet, low-pressure activity with soft pacing.",
        "speed": 0.65,
        "difficulty": 0.25,
        "duration": 90,
    },
    "anger": {
        "game": "break-blocks",
        "title": "Break the Blocks",
        "message": "A short, controlled release game with clear feedback.",
        "speed": 1.05,
        "difficulty": 0.45,
        "duration": 60,
    },
    "fear": {
        "game": "breathing-orbs",
        "title": "Breathing Orbs",
        "message": "A slow visual rhythm designed for a gentler interaction.",
        "speed": 0.55,
        "difficulty": 0.15,
        "duration": 75,
    },
    "surprise": {
        "game": "quick-reaction",
        "title": "Quick Reaction",
        "message": "A playful reaction game for alert, high-energy moments.",
        "speed": 1.35,
        "difficulty": 0.65,
        "duration": 45,
    },
    "disgust": {
        "game": "clear-the-space",
        "title": "Clear the Space",
        "message": "A satisfying tidy-up game with simple, repeatable actions.",
        "speed": 0.9,
        "difficulty": 0.35,
        "duration": 60,
    },
    "neutral": {
        "game": "memory-match",
        "title": "Memory Match",
        "message": "A balanced mini-game for a neutral or mixed mood.",
        "speed": 1.0,
        "difficulty": 0.5,
        "duration": 75,
    },
}


KEYWORD_FALLBACK: dict[str, tuple[str, ...]] = {
    "joy": (
        "happy",
        "great",
        "excited",
        "joy",
        "amazing",
        "good",
        "delighted",
        "wonderful",
    ),
    "sadness": (
        "sad",
        "down",
        "lonely",
        "unhappy",
        "hurt",
        "cry",
        "depressed",
        "miserable",
    ),
    "anger": (
        "angry",
        "furious",
        "annoyed",
        "frustrated",
        "mad",
        "irritated",
        "rage",
    ),
    "fear": (
        "afraid",
        "scared",
        "anxious",
        "worried",
        "nervous",
        "stressed",
        "overwhelmed",
        "panic",
    ),
    "surprise": (
        "surprised",
        "shocked",
        "unexpected",
        "wow",
        "astonished",
    ),
    "disgust": (
        "disgusted",
        "gross",
        "repulsed",
        "sick of",
        "revolting",
    ),
}


LABEL_ALIASES = {
    "happy": "joy",
    "happiness": "joy",
    "sad": "sadness",
    "angry": "anger",
    "scared": "fear",
    "anxiety": "fear",
}


def normalise_label(label: str) -> str:
    cleaned = label.strip().lower()
    return LABEL_ALIASES.get(cleaned, cleaned)


def fallback_classify(text: str) -> list[dict[str, float | str]]:
    lower_text = text.lower()

    scores: dict[str, float] = {
        label: 0.02 for label in GAME_PROFILES
    }
    scores["neutral"] = 0.15

    for label, keywords in KEYWORD_FALLBACK.items():
        hits = sum(1 for keyword in keywords if keyword in lower_text)

        if hits:
            scores[label] += 0.55 + min(0.25, hits * 0.08)

    total = sum(scores.values())

    return [
        {
            "label": label,
            "score": score / total,
        }
        for label, score in sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]


def load_classifier() -> Pipeline | None:
    try:
        logger.info("Loading local Transformers model: %s", HF_MODEL)

        model_pipeline = pipeline(
            task="text-classification",
            model=HF_MODEL,
            top_k=None,
            device=MODEL_DEVICE,
        )

        logger.info("Emotion model loaded successfully.")
        return model_pipeline

    except Exception:
        logger.exception(
            "Could not load the Transformers model. "
            "MoodPlay will use its keyword fallback classifier."
        )
        return None


def classify_locally(text: str) -> list[dict[str, Any]]:
    if classifier is None:
        return fallback_classify(text)

    try:
        raw_result = classifier(text)

        # With top_k=None, Transformers commonly returns:
        # [[{"label": "...", "score": ...}, ...]]
        if (
            isinstance(raw_result, list)
            and raw_result
            and isinstance(raw_result[0], list)
        ):
            raw_result = raw_result[0]

        if not isinstance(raw_result, list):
            raise ValueError("Unexpected model response format.")

        cleaned: list[dict[str, Any]] = []

        for item in raw_result:
            if not isinstance(item, dict):
                continue

            label = item.get("label")
            score = item.get("score")

            if label is None or score is None:
                continue

            cleaned.append(
                {
                    "label": normalise_label(str(label)),
                    "score": float(score),
                }
            )

        if not cleaned:
            raise ValueError("The model returned no usable predictions.")

        return sorted(
            cleaned,
            key=lambda item: float(item["score"]),
            reverse=True,
        )

    except Exception:
        logger.exception(
            "Local model inference failed. Using keyword fallback."
        )
        return fallback_classify(text)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global classifier

    # Loading during startup means the first API request does not need to
    # initialise the model.
    classifier = await run_in_threadpool(load_classifier)

    yield

    classifier = None


app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "model": HF_MODEL,
        "inference": "transformers-local" if classifier else "keyword-fallback",
    }


@app.post("/api/analyse")
async def analyse(request: MoodRequest) -> dict[str, Any]:
    text = request.text.strip()

    if len(text) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please describe how you feel.",
        )

    # Transformers inference is blocking, so run it outside the async
    # event loop.
    scores = await run_in_threadpool(classify_locally, text)

    top_result = scores[0]
    detected_label = normalise_label(str(top_result["label"]))

    mood = (
        detected_label
        if detected_label in GAME_PROFILES
        else "neutral"
    )

    return {
        "mood": mood,
        "confidence": round(float(top_result["score"]), 4),
        "scores": [
            {
                "label": normalise_label(str(item["label"])),
                "score": round(float(item["score"]), 4),
            }
            for item in scores[:7]
        ],
        "game": GAME_PROFILES[mood],
        "model": HF_MODEL if classifier else "keyword-fallback",
        "disclaimer": (
            "MoodPlay estimates emotional cues from text. "
            "It does not determine or diagnose a person's true emotional state."
        ),
    }


@app.get("/")
def index() -> FileResponse:
    index_file = STATIC_DIR / "index.html"

    if not index_file.is_file():
        raise HTTPException(
            status_code=500,
            detail="Frontend file static/index.html was not found.",
        )

    return FileResponse(index_file)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR, check_dir=False),
    name="static",
)