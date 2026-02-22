import base64
import os
import shutil
from typing import List
from .models import DetectionInfo, ObjectDetectionResult


class ObjectDetectionService:
    _model = None
    MODEL_NAME = "yolo26m.pt"
    MODEL_DIR = "models"
    MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

    @classmethod
    def get_model(cls):
        """Load the YOLO model, downloading it if necessary."""
        try:
            from ultralytics import YOLO
        except ImportError:
            raise RuntimeError(
                "Object Detection dependencies (ultralytics) are not available in this environment."
            )

        if cls._model is None:
            if not os.path.exists(cls.MODEL_PATH):
                os.makedirs(cls.MODEL_DIR, exist_ok=True)
                try:
                    # Attempt to load/download
                    model = YOLO(cls.MODEL_NAME)  # noqa: F841
                    # If it was downloaded to the current directory, move it to MODEL_DIR
                    if (
                        os.path.exists(cls.MODEL_NAME)
                        and cls.MODEL_PATH != cls.MODEL_NAME
                    ):
                        # Check if target already exists (unlikely given the if not exists check above)
                        if os.path.exists(cls.MODEL_PATH):
                            os.remove(cls.MODEL_PATH)
                        shutil.move(cls.MODEL_NAME, cls.MODEL_PATH)
                    cls._model = YOLO(cls.MODEL_PATH)
                except Exception as e:
                    # Fallback or re-raise with better message
                    raise RuntimeError(
                        f"Failed to load or download model {cls.MODEL_NAME}: {str(e)}"
                    )
            else:
                cls._model = YOLO(cls.MODEL_PATH)
        return cls._model

    @classmethod
    def detect(
        cls, image_bytes: bytes, object_names: List[str], threshold: float
    ) -> ObjectDetectionResult:
        """
        Perform object detection on the image and filter by object_names.
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            raise RuntimeError(
                "Object Detection dependencies (OpenCV/NumPy) are not available in this environment."
            )

        # Load image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Invalid image format or empty image")

        model = cls.get_model()

        # Map object names to class IDs (case-insensitive)
        names = model.names  # dict of {id: name}
        name_to_id = {v.lower(): k for k, v in names.items()}

        target_ids = []
        for obj in object_names:
            obj_lower = obj.lower()
            if obj_lower in name_to_id:
                target_ids.append(name_to_id[obj_lower])

        # Perform inference
        if target_ids:
            # Only detect the requested classes
            results = model.predict(
                img, conf=threshold, classes=target_ids, verbose=False
            )[0]
        else:
            # If no requested objects are known by the model, we run with a very high threshold
            # to get an empty results object that still allows calling .plot()
            results = model.predict(img, conf=1.1, verbose=False)[0]

        # Initialize detections with count 0 for all requested objects
        detections_data = {obj: {"count": 0, "boxes": []} for obj in object_names}

        # Process results
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name_found = names[cls_id]

            # Match back to the requested object name (case-insensitive)
            for obj in object_names:
                if obj.lower() == class_name_found.lower():
                    coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    detections_data[obj]["count"] += 1
                    detections_data[obj]["boxes"].append(coords + [conf])

        # Annotate image
        annotated_img = results.plot()

        # Convert to JPEG
        _, buffer = cv2.imencode(".jpg", annotated_img)
        base64_image = base64.b64encode(buffer).decode("utf-8")

        # Format detection info
        formatted_detections = {
            obj: DetectionInfo(count=data["count"], boxes=data["boxes"])
            for obj, data in detections_data.items()
        }

        return ObjectDetectionResult(
            detections=formatted_detections, annotated_image=base64_image
        )
