from __future__ import annotations

from roboto import Dataset, File, InvocationContext, RobotoClient
from roboto.ai.chat import Chat
from roboto.ai.core import RobotoLLMContext

from .prompts import FINAL_RESPONSE_SECTION_HEADER, SYSTEM_PROMPT

CHAT_TIMEOUT_SECONDS = 3.0 * 60  # 3 minutes


def _extract_final_response(transcript: str) -> str:
    """Return the final response section if present; otherwise return the full transcript."""
    if FINAL_RESPONSE_SECTION_HEADER not in transcript:
        return transcript
    _, tail = transcript.split(FINAL_RESPONSE_SECTION_HEADER, 1)
    return tail.strip()


class ChatInterface:
    def __init__(self, org_id: str, roboto_client: RobotoClient):
        self.org_id = org_id
        self.roboto_client = roboto_client

    @classmethod
    def from_invocation_context(cls, ctx: InvocationContext) -> "ChatInterface":
        return cls(org_id=ctx.org_id, roboto_client=ctx.roboto_client)

    def prompt_with(self, dataset: Dataset, recordings: list[File] | None = None) -> str:
        dataset_id = dataset.dataset_id
        file_ids = [f.file_id for f in (recordings or [])]

        llm_ctx = RobotoLLMContext(dataset_ids=[dataset_id], file_ids=file_ids)

        chat = Chat.start(
            message=f"Please analyze dataset {dataset_id}.",
            context=llm_ctx,
            system_prompt=SYSTEM_PROMPT,
            org_id=self.org_id,
            roboto_client=self.roboto_client,
        )

        chat.await_user_turn(tick=1, timeout=CHAT_TIMEOUT_SECONDS)

        transcript = (chat.transcript or "").strip()
        if not transcript:
            raise ValueError(f"AI chat returned an empty transcript for dataset {dataset_id}.")

        return _extract_final_response(transcript)
