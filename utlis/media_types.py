from enum import Enum

class MediaType(str,Enum):
    Image = "image"
    Video = "video"
    Audio = "audio"
    Document = "application"