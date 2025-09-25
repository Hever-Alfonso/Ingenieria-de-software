# ============================================
# poc/experiences/services.py
# ============================================

from __future__ import annotations
import os
import textwrap
from typing import List, Dict, Any
from django.conf import settings
from .models import Enterprise
from google import genai
from google.genai import types
import logging

def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta GEMINI_API_KEY en el entorno.")

    return genai.Client()

def get_config() -> Dict[str, Any]:
    cfg = getattr(settings, "GENAI_CONFIG", {}) # Obtener configuración desde settings.py
    thinking_cfg = cfg.get("thinking_config", {}) # Configuración de 'thinking'

    # Construir y devolver configuración completa
    return types.GenerateContentConfig(
        temperature=cfg.get("temperature", 0.2),
        max_output_tokens=cfg.get("max_output_tokens", 600),
        thinking_config=types.ThinkingConfig(**thinking_cfg),
    )

def build_corpus(enterprise: Enterprise, max_chars: int = 18000) -> str:
    """Corpus condensado de todas las reviews de la empresa."""
    reviews = [] # Lista que contendrá cada review formateada
    qs = enterprise.reviews.order_by("-created_at").values(
        "title", "body", "rating", "anonymous", "created_at", "author__username"
    ) # QuerySet optimizado

    # Para cada review, formatear y añadir a la lista
    for r in qs:
        created = r["created_at"].strftime("%Y-%m-%d")
        reviews.append(
            textwrap.dedent(
                f"""\
                - Review:
                    título: {r["title"]}
                    rating: {r["rating"]}⭐
                    fecha: {created}
                    texto: {r["body"]}
                """
            )
        )

    # Unir todas las reviews en un solo string y truncar si es necesario
    corpus = "\n".join(reviews).strip()
    if len(corpus) > max_chars:
        corpus = corpus[:max_chars] + "\n\n[TRUNCADO]"

    return corpus

def build_prompt(enterprise: Enterprise, corpus: str) -> str:
    """Prompt en español para un resumen ejecutivo claro y equilibrado."""
    return textwrap.dedent(
        f"""\
        Eres un analista que resume experiencias de usuarios sobre empresas.
        Genera un RESUMEN claro y equilibrado con base en todas las reviews para la empresa "{enterprise.name}".

        Reglas:
        - Idioma: español.
        - Extensión: ~8-10 frases, estilo ejecutivo.
        - Estilo: Un parrafo. No negritas ni estilos adicionales. Solo texto plano.
        - Incluye: puntos fuertes, puntos a mejorar, patrones recurrentes (positivos/negativos) y una conclusión breve.
        - No inventes: usa únicamente el texto proporcionado.
        - Evita datos personales o identificar usuarios.

        Reviews (extracto):
        {corpus}
        """
    )

def summarize_enterprise_reviews(enterprise: Enterprise) -> str:
    """
    Llama a Gemini y devuelve el resumen (no persiste).
    """

    try:
        # Construir corpus y prompt
        corpus = build_corpus(enterprise)
        prompt = build_prompt(enterprise, corpus)

        # Obtener cliente y configuración
        client = get_client()
        model = os.environ.get("GEMINI_MODEL")
        config = get_config()

        # Llamar a la API de generación de contenido
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        # Extraer y devolver el texto generado
        summary = resp.text.strip()
        return summary

    except Exception as e:
        raise RuntimeError(f"Error al generar resumen: {e}")

def update_enterprise_summary(enterprise_id: int) -> None:
    """
    Recalcula y persiste el resumen en Enterprise.AI_summary.
    Maneja ausencia de reviews y errores de red/SDK.
    """
    try:
        # Obtener empresa y verificar reviews
        enterprise = Enterprise.objects.get(pk=enterprise_id)

        # Si no hay reviews, limpiar resumen y salir
        if not enterprise.reviews.exists() or enterprise.reviews.count() == 0:
            enterprise.AI_summary = ""
            enterprise.save(update_fields=["AI_summary"])
            return

        # Generar nuevo resumen
        summary = summarize_enterprise_reviews(enterprise)
        if not summary:
            summary = "Aún no hay suficiente información para generar un resumen fiable."

        # Guardar resumen
        enterprise.AI_summary = summary
        enterprise.save(update_fields=["AI_summary"])

    except Exception as e:
        Enterprise.objects.filter(pk=enterprise_id).update(
            AI_summary="No fue posible actualizar el resumen en este momento."
        )
        logging.error(f"Error al actualizar resumen para Enterprise {enterprise_id}: {e}")