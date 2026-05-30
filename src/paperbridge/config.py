from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    api_key: str | None
    base_url: str | None
    llm_model: str | None
    vlm_model: str | None
    vlm_api_key: str | None = None
    vlm_base_url: str | None = None
    timeout_seconds: float = 60.0
    max_tokens: int = 4096

    @classmethod
    def from_env(cls) -> "LLMConfig":
        timeout_raw = os.getenv("PAPERBRIDGE_OPENAI_TIMEOUT", "60")
        try:
            timeout_seconds = max(5.0, float(timeout_raw))
        except ValueError:
            timeout_seconds = 60.0
        max_tokens_raw = os.getenv("PAPERBRIDGE_OPENAI_MAX_TOKENS", "4096")
        try:
            max_tokens = max(256, int(max_tokens_raw))
        except ValueError:
            max_tokens = 4096
        api_key = os.getenv("PAPERBRIDGE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("PAPERBRIDGE_OPENAI_BASE_URL")
        return cls(
            api_key=api_key,
            base_url=base_url,
            llm_model=os.getenv("PAPERBRIDGE_LLM_MODEL"),
            vlm_model=os.getenv("PAPERBRIDGE_VLM_MODEL"),
            vlm_api_key=os.getenv("PAPERBRIDGE_VLM_API_KEY") or api_key,
            vlm_base_url=os.getenv("PAPERBRIDGE_VLM_BASE_URL") or base_url,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
        )

    def can_use_llm(self) -> bool:
        return bool(self.api_key and self.llm_model)

    def can_use_vlm(self) -> bool:
        return bool(self.vlm_api_key and self.vlm_model)


@dataclass(frozen=True)
class ConvertOptions:
    formats: set[str]
    profile: str = "full"
    dpi: int = 200
    max_pages: int | None = None
    use_llm: bool = True
    use_vlm: bool = False
    debug: bool = False
    force: bool = False
    quiet: bool = False
