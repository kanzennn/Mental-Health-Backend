from pydantic import BaseModel


class TranscriberResponse(BaseModel):
    text: str
    audio_duration_s: float
    processing_s: float
    rtf: float
