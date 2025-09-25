"""Seleção de destaques usando LLM ou heurísticas."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

from ..config import get_settings
from ..observability.metrics import llm_calls_total
from .schemas import HighlightClip, HighlightPlan


@dataclass
class HighlightSelectorParams:
    max_clips: int
    min_clip_sec: int
    max_clip_sec: int
    llm_style: str
    language: str


class HighlightSelector:
    """Seleciona clipes interessantes a partir da transcrição."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def _llm_available(self) -> bool:
        return bool(self.settings.openai_api_key)

    def select(self, transcript: List[str], duration: float, params: HighlightSelectorParams) -> HighlightPlan:
        if self._llm_available():
            try:
                return self._select_via_llm(transcript, duration, params)
            except Exception:
                llm_calls_total.labels(provider="openai", status="error").inc()
        return self._select_heuristic(transcript, duration, params)

    def _select_via_llm(
        self, transcript: List[str], duration: float, params: HighlightSelectorParams
    ) -> HighlightPlan:
        import openai

        client = openai.OpenAI(api_key=self.settings.openai_api_key)
        prompt = self._build_prompt(transcript, duration, params)
        response = client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um editor experiente de vídeos virais. Escolha trechos "
                        "impactantes e retorne apenas JSON válido com a estrutura {clips: []}."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        llm_calls_total.labels(provider="openai", status="success").inc()
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        plan = HighlightPlan.model_validate(data)
        return plan.clamp(duration, params.min_clip_sec, params.max_clip_sec, params.max_clips)

    def _build_prompt(self, transcript: List[str], duration: float, params: HighlightSelectorParams) -> str:
        joined = "\n".join(transcript)
        prompt = (
            f"DURAÇÃO TOTAL: {duration:.2f}s\n"
            f"PARÂMETROS: max_clips={params.max_clips}, estilo={params.llm_style}, idioma={params.language}\n"
            "TRANSCRIÇÃO:\n"
            f"{joined}\n"
            "RETORNE JSON COM LISTA DE CLIPES."\
        )
        return prompt

    def _select_heuristic(self, transcript: List[str], duration: float, params: HighlightSelectorParams) -> HighlightPlan:
        """Fallback simples baseado em heurísticas básicas."""

        chunk_length = max(params.min_clip_sec, 10)
        num_chunks = max(1, int(duration // chunk_length))
        if not transcript:
            transcript = ["Trecho não disponível"]
        per_chunk = max(1, len(transcript) // max(1, num_chunks))
        cursor = 0.0
        clips: List[HighlightClip] = []
        for idx in range(min(params.max_clips, len(transcript))):
            text = transcript[min(idx * per_chunk, len(transcript) - 1)].strip()
            start = cursor
            end = min(duration, start + chunk_length)
            clips.append(
                HighlightClip(
                    start_sec=start,
                    end_sec=end,
                    title=f"Momento {idx + 1}",
                    description=text[:150],
                    tags=[params.llm_style],
                    confidence=0.4 + 0.1 * idx,
                    reason="Selecionado por heurística",
                )
            )
            cursor = end
            if cursor >= duration:
                break
        plan = HighlightPlan(clips=clips)
        return plan.clamp(duration, params.min_clip_sec, params.max_clip_sec, params.max_clips)


__all__ = ["HighlightSelector", "HighlightSelectorParams"]
