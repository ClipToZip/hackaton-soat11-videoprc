from pydantic import BaseModel

class VideoEntity(BaseModel):
    video_id: str
    path: str