import io

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from tf_keras.models import load_model  # legacy Keras 2 loader - Teachable Machine models need this

router = APIRouter()

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model and labels once at import time (not on every request)
model = load_model("model/keras_model.h5", compile=False)
class_names = open("model/labels.txt", "r").readlines()


def predict_image(image: Image.Image) -> dict:
    image = image.convert("RGB")

    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    # turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Predicts the model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index][2:].strip()  # strip the leading "0 " index label
    confidence_score = float(prediction[0][index])

    return {"class_name": class_name, "confidence_score": confidence_score}


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents))
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="File is not a valid image")

    return predict_image(image)


if __name__ == "__main__":
    # Quick standalone test - run `python keras1.py` to try the model on a
    # sample image without starting the FastAPI server.
    test_image_path = "images/watch.jpg"
    test_image = Image.open(test_image_path).convert("RGB")
    result = predict_image(test_image)
    print(f"Class: {result['class_name']}")
    print(f"Confidence Score: {result['confidence_score']}")
