import imutils
import cv2
from PIL import Image
import numpy as np

def resize_to_fit(image, width, height):
    """
    A helper function to resize an image to fit within a given size
    :param image: image to resize
    :param width: desired width in pixels
    :param height: desired height in pixels
    :return: the resized image
    """

    # grab the dimensions of the image, then initialize
    # the padding values
    (h, w) = image.shape[:2]

    # if the width is greater than the height then resize along
    # the width
    if w > h:
        image = imutils.resize(image, width=width)

    # otherwise, the height is greater than the width so resize
    # along the height
    else:
        image = imutils.resize(image, height=height)

    # determine the padding values for the width and height to
    # obtain the target dimensions
    padW = int((width - image.shape[1]) / 2.0)
    padH = int((height - image.shape[0]) / 2.0)

    # pad the image then apply one more resizing to handle any
    # rounding issues
    image = cv2.copyMakeBorder(image, padH, padH, padW, padW,
        cv2.BORDER_REPLICATE)
    image = cv2.resize(image, (width, height))

    # return the pre-processed image
    return image

def get_background():
    background = Image.open('background2.jpg')
    background = background.convert("RGBA")
    datas = background.getdata()
    new_data = []
    for item in datas:
        # change all white (also shades of whites)
        # pixels to transparent
        if all([x > 200 and x < 256 for x in item[:3]]):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    background.putdata(new_data)
    background = np.array(background)
    background = cv2.cvtColor(background, cv2.COLOR_RGB2BGR)
    #cv2.imshow('Image', background)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return background

def preprocess_image(captcha_image_file,background):
    # Load the image
    image = cv2.imread(captcha_image_file)
    return preprocess_image2(image,background)

def preprocess_image2(image,background):
    # Subtract the images
    image = cv2.subtract(background,image)

    #convert it to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # invert
    image = cv2.bitwise_not(image)

    # Threshold the image to binary using Otsu's method
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Define a kernel for the dilation operation
    kernel = np.ones((2,2), np.uint8)

    # Dilate the image to fill in crevices in the letters
    image = cv2.dilate(binary, kernel, iterations=1)
    # invert
    image = cv2.bitwise_not(image)
    #cv2.imshow('Image', image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #exit()
    return image