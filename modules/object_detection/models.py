from typing import List, Dict
from pydantic import BaseModel


class DetectionInfo(BaseModel):
    count: int
    boxes: List[List[float]]


class ObjectDetectionResult(BaseModel):
    detections: Dict[str, DetectionInfo]
    annotated_image: str
