from ultralytics import YOLO

# Load the YOLO26 model
model = YOLO("models/yolo26m.pt")

# Export the model to ONNX format
model.export(format="onnx")  # creates 'yolo26n.onnx'

# Load the exported ONNX model
onnx_model = YOLO("models/yolo26m.onnx")

# Run inference
results = onnx_model.predict("https://ultralytics.com/images/bus.jpg",save=True)
