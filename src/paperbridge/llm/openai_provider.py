from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from openai import OpenAI

from paperbridge.config import LLMConfig
from paperbridge.llm.base import LLMConfigurationError, LLMPageInput, LLMProviderError, PageStructureResponse


class OpenAICompatibleProvider:
    def __init__(self, config: LLMConfig, output_dir: Path | None = None) -> None:
        if not config.api_key:
            raise LLMConfigurationError("PAPERBRIDGE_OPENAI_API_KEY or OPENAI_API_KEY is required")
        self.config = config
        self.output_dir = output_dir
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url, timeout=config.timeout_seconds)

    def structure_page(self, page_input: LLMPageInput, use_vlm: bool = False) -> PageStructureResponse:
        model = self.config.vlm_model if use_vlm else self.config.llm_model
        if not model:
            variable = "PAPERBRIDGE_VLM_MODEL" if use_vlm else "PAPERBRIDGE_LLM_MODEL"
            raise LLMConfigurationError(f"{variable} is required")

        prompt = _build_prompt(page_input)
        content: str | list[dict[str, Any]]
        if use_vlm and page_input.page_image_path:
            image_url = self._image_data_url(page_input.page_image_path)
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        else:
            content = prompt

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You classify PDF text blocks into a strict JSON structure. "
                            "Do not rewrite, invent, or delete PDF text. Unknown content must be marked unknown."
                        ),
                    },
                    {"role": "user", "content": content},
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=self.config.max_tokens,
            )
        except Exception as exc:  # pragma: no cover - external API
            raise LLMProviderError(str(exc)) from exc

        payload = response.choices[0].message.content or "{}"
        try:
            return PageStructureResponse.model_validate(json.loads(payload))
        except Exception as exc:
            raise LLMProviderError(f"Invalid LLM JSON response: {exc}") from exc

    def _image_data_url(self, page_image_path: str) -> str:
        if not self.output_dir:
            raise LLMConfigurationError("output_dir is required for VLM page image input")
        path = self.output_dir / page_image_path
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{data}"


def _build_prompt(page_input: LLMPageInput) -> str:
    raw_blocks = [block.model_dump() for block in page_input.raw_blocks]
    schema = PageStructureResponse.model_json_schema()
    return json.dumps(
        {
            "task": "Classify raw PDF text blocks into document structure blocks.",
            "rules": [
                "Return strict JSON matching the schema.",
                "Every output block must reference one or more provided raw_block ids.",
                "The text field must be copied from provided raw blocks without paraphrasing.",
                "Headers, footers, and page numbers must not be placed in body reading order.",
                "If uncertain, use type unknown.",
            ],
            "page_number": page_input.page_number,
            "raw_blocks": raw_blocks,
            "schema": schema,
        },
        ensure_ascii=False,
    )
