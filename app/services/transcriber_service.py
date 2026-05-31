import httpx
from app.core.config import settings
from app.schemas.transcriber_schema import TranscriberResponse


class TranscriberService:
    def __init__(self):
        self.ai_api_url = settings.AI_API_URL

    async def transcribe_audio(self, audio_file) -> TranscriberResponse:
        async with httpx.AsyncClient(timeout=60) as client:
            files = {
                "file": (
                    audio_file.filename,
                    await audio_file.read(),
                    audio_file.content_type,
                )
            }
            response = await client.post(
                f"{self.ai_api_url}/transcribe",
                files=files,
            )
            response.raise_for_status()
            return TranscriberResponse(**response.json())
