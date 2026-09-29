import logging
import os
import smtplib
import uuid
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from redis import Redis
from rq import Queue
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from ..email_service import send_email
from ..planetiler_job import _validate_request, process_map
from ..translations import DEFAULT_LANGUAGE, Lang, get_texts

router = APIRouter()
logger = logging.getLogger(__name__)


class MapRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    url: HttpUrl
    email: EmailStr
    lang: Lang = DEFAULT_LANGUAGE


def _confirmation_serializer() -> URLSafeTimedSerializer:
    secret = os.environ.get("CONFIRMATION_SECRET", "")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servei de confirmació no està configurat",
        )
    return URLSafeTimedSerializer(secret, salt="map-request-confirmation-v1")


def _redis_queue() -> tuple[Redis, Queue]:
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    connection = Redis.from_url(redis_url)
    return connection, Queue(connection=connection)


@router.post("/mapes/requests", status_code=status.HTTP_202_ACCEPTED)
def sol_licitar_mapa(request: MapRequest):
    texts = get_texts(request.lang)
    try:
        name, url = _validate_request(request.name, str(request.url))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e

    token_id = uuid.uuid4().hex
    token = _confirmation_serializer().dumps(
        {
            "id": token_id,
            "name": name,
            "url": url,
            "email": str(request.email),
            "lang": request.lang,
        }
    )
    public_url = os.environ.get("APP_PUBLIC_URL", "https://trackio.es/api").rstrip("/")
    confirmation_url = f"{public_url}/mapes/confirm?token={quote(token, safe='')}"

    try:
        send_email(
            str(request.email),
            texts["confirm_subject"],
            texts["confirm_body"].format(confirmation_url=confirmation_url),
        )
    except (OSError, RuntimeError, smtplib.SMTPException) as e:
        logger.exception("No s'ha pogut enviar el correu de confirmació")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=texts["err_email_confirmation"],
        ) from e

    return {
        "message": texts["request_success_message"],
        "expires_in_seconds": 86400,
    }


@router.get("/mapes/confirm", response_class=HTMLResponse)
def mostrar_confirmacio(token: str = Query(min_length=1, max_length=4096)):
    token_ttl = int(os.environ.get("CONFIRMATION_TOKEN_TTL_SECONDS", "86400"))
    try:
        payload = _confirmation_serializer().loads(token, max_age=token_ttl)
        _validate_request(payload["name"], payload["url"])
    except SignatureExpired as e:
        texts = get_texts(None)
        raise HTTPException(status_code=410, detail=texts["err_expired"]) from e
    except (BadSignature, KeyError, TypeError, ValueError) as e:
        texts = get_texts(None)
        raise HTTPException(status_code=400, detail=texts["err_invalid"]) from e

    lang = payload.get("lang")
    texts = get_texts(lang)

    return HTMLResponse(
        content=(
            f"<!doctype html><html lang='{lang or DEFAULT_LANGUAGE}'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{texts['page_title']}</title>"
            f"<h1>{texts['page_heading']}</h1>"
            f"<p>{texts['page_text']}</p>"
            f"<form method='post' action='?token={quote(token, safe='')}'>"
            f"<button type='submit'>{texts['page_button']}</button></form></html>"
        )
    )


@router.post("/mapes/confirm")
def confirmar_sol_licitud(token: str = Query(min_length=1, max_length=4096)):
    serializer = _confirmation_serializer()
    token_ttl = int(os.environ.get("CONFIRMATION_TOKEN_TTL_SECONDS", "86400"))
    try:
        payload = serializer.loads(token, max_age=token_ttl)
        name, url, email, token_id = (
            payload["name"],
            payload["url"],
            payload["email"],
            payload["id"],
        )
        _validate_request(name, url)
    except SignatureExpired as e:
        texts = get_texts(None)
        raise HTTPException(status_code=410, detail=texts["err_expired"]) from e
    except (BadSignature, KeyError, TypeError, ValueError) as e:
        texts = get_texts(None)
        raise HTTPException(status_code=400, detail=texts["err_invalid"]) from e

    texts = get_texts(payload.get("lang"))

    connection, queue = _redis_queue()
    used_key = f"map-request-confirmed:{token_id}"
    try:
        if not connection.set(used_key, "1", nx=True, ex=token_ttl):
            raise HTTPException(status_code=409, detail=texts["err_already_confirmed"])

        queue_position = queue.count + 1
        try:
            job = queue.enqueue(
                process_map,
                name,
                url,
                token_id,
                email,
                job_id=token_id,
                result_ttl=86400,
                failure_ttl=86400,
                job_timeout=2400
            )
        except Exception:
            connection.delete(used_key)
            raise
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("No s'ha pogut posar la sol·licitud a la cua")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=texts["err_queue"],
        ) from e
    finally:
        connection.close()

    try:
        send_email(
            email,
            texts["queued_subject"],
            texts["queued_body"].format(
                name=name, queue_position=queue_position, job_id=job.id
            ),
        )
    except (OSError, RuntimeError, smtplib.SMTPException):
        logger.exception(
            "La tasca %s és a la cua, però no s'ha pogut enviar l'avís", job.id
        )

    return {
        "message": texts["queued_success_message"],
        "task_id": job.id,
        "estimated_queue_position": queue_position,
    }
