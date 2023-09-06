from flask import Flask, request, jsonify
from keras.models import load_model
from helpers import resize_to_fit, get_background, preprocess_image, preprocess_image2
from imutils import paths
import numpy as np
import imutils
import cv2
import pickle
from flasgger import Swagger
from flask_healthz import healthz
from flask_healthz import HealthError

MODEL_FILENAME = "self_captcha_model2.hdf5"
MODEL_LABELS_FILENAME = "self_model_labels2.dat"
CAPTCHA_IMAGE_FOLDER = "self_generated_captcha_images2"

print("Application is starting...")
app = Flask(__name__)
app.register_blueprint(healthz, url_prefix="/healthz")
app.config['SWAGGER'] = {
    'title': 'Captcha Recognition',
    'openapi': '3.0.2'
}
swagger = Swagger(app)

background = get_background()

app.config.update(
    HEALTHZ = {
        "live": "app.liveness",
    }
)
def liveness():
    pass

def recognize(filestr):
    # Convert string data to numpy array
    npimg = np.fromstring(filestr, np.uint8)

    # Convert numpy array to image
    image_file = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # load preprocessed image
    image = preprocess_image2(image_file,background)

    # Add some extra padding around the image
    image = cv2.copyMakeBorder(image, 20, 20, 20, 20, cv2.BORDER_REPLICATE)

    # threshold the image (convert it to pure black and white)
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # find the contours (continuous blobs of pixels) the image
    contours = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Hack for compatibility with different OpenCV versions
    contours = contours[1] if imutils.is_cv3() else contours[0]

    letter_image_regions = []

    # Now we can loop through each of the four contours and extract the letter
    # inside of each one
    for contour in contours:
        #print (contour)
        # Get the rectangle that contains the contour
        (x, y, w, h) = cv2.boundingRect(contour)

        # Compare the width and height of the contour to detect letters that
        # are conjoined into one chunk
        if w / h > 1.25:
            # This contour is too wide to be a single letter!
            # Split it in half into two letter regions!
            half_width = int(w / 2)
            letter_image_regions.append((x, y, half_width, h))
            letter_image_regions.append((x + half_width, y, half_width, h))
        else:
            # This is a normal letter by itself
            letter_image_regions.append((x, y, w, h))

    # If we found more or less than 4 letters in the captcha, our letter extraction
    # didn't work correcly. Skip the image instead of saving bad training data!
    print (len(letter_image_regions))
    if len(letter_image_regions) != 4:
        return("not enough letters recognized")

    # Sort the detected letter images based on the x coordinate to make sure
    # we are processing them from left-to-right so we match the right image
    # with the right letter
    letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])

    # Create an output image and a list to hold our predicted letters
    output = cv2.merge([image] * 3)
    predictions = []

    # loop over the lektters
    for letter_bounding_box in letter_image_regions:
        # Grab the coordinates of the letter in the image
        x, y, w, h = letter_bounding_box

        # Extract the letter from the original image with a 2-pixel margin around the edge
        letter_image = image[y - 2 : y + h + 2, x - 2 : x + w + 2]

        # Re-size the letter image to 20x20 pixels to match training data
        letter_image = resize_to_fit(letter_image, 20, 20)

        # Turn the single image into a 4d list of images to make Keras happy
        letter_image = np.expand_dims(letter_image, axis=2)
        letter_image = np.expand_dims(letter_image, axis=0)

        # Ask the neural network to make a prediction
        prediction = model.predict(letter_image)

        # Convert the one-hot-encoded prediction back to a normal letter
        letter = lb.inverse_transform(prediction)[0]
        predictions.append(letter)

        # draw the prediction on the output image
        cv2.rectangle(output, (x - 2, y - 2), (x + w + 4, y + h + 4), (0, 255, 0), 1)
        cv2.putText(
            output,
            letter,
            (x - 5, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
        )

    # Print the captcha's text
    captcha_text = "".join(predictions)
    print("CAPTCHA text is: {}".format(captcha_text))
    return captcha_text;

@app.route('/api/recognize', methods=['POST'])
def recognise_image():
    """
    ---
    description: Returns recognized String from captcha image
    tags:
    - image

    requestBody:
      content:
        multipart/form-data:
          schema:
            type: object
            properties: 
              image:
                description: Captcha image.
                type: file
      required: true
    responses:
      200:
        description: A captcha String
    """
    if 'image' not in request.files:
        return "No 'image' key in request.files"


    filestr = request.files['image'].read()
    # Assuming you're receiving the image as a file, you may want to convert the data to an appropriate format for your recognize function
    # Depending on your recognize function, you might need to do things differently.

    text = recognize(filestr)
    return text if text else "No text recognized"

# Load up the model labels (so we can translate model predictions to actual letters)
with open(MODEL_LABELS_FILENAME, "rb") as f:
    lb = pickle.load(f)

# Load the trained neural network
model = load_model(MODEL_FILENAME)


if __name__ == '__main__':
    app.run(port=8000, debug=False)
