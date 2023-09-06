import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
from perlin_noise import PerlinNoise
import numpy as np

# Define captcha dimensions
width = 200
height = 70

# Define captcha length
captcha_length = 4

# Define Perlin noise parameters
noise = PerlinNoise(octaves=4, seed=10)
scale = 20.0

# Define font
font1 = ImageFont.truetype("georgia.ttf", size=40)
font2 = ImageFont.truetype("impact.ttf", size=40)
#font3 = ImageFont.truetype("Tahoma_Bold.ttf", size=40)
#font3 = ImageFont.truetype("tahoma.ttf", size=40)
font3 = ImageFont.truetype("Warownia.otf", size=40)


# Define output folder
output_folder = "self_generated_captcha_images2"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Generate 10000 captcha images
for i in range(10000):
    # Generate random captcha text
    captcha_text = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=captcha_length)
    )

    # Create a new image
    image = Image.new("RGB", (width, height), color=(255, 255, 255))

    # Get a drawing context
    draw = ImageDraw.Draw(image)

    # Add Perlin noise to the image
    #perlin_noise = np.zeros((height, width))
    #for y in range(height):
    #    for x in range(width):
    #        perlin_noise[y][x] = noise([x / scale, y / scale, i / scale])
    #perlin_noise = np.uint8(
    #    np.interp(perlin_noise, (np.min(perlin_noise), np.max(perlin_noise)), (0, 255))
    #)
    #noise_image = Image.fromarray(perlin_noise)
    #noise_image = noise_image.convert("RGB")

    # print("Image Size: ", image.mode)
    # print("Noise Image Size: ", noise_image.mode)
    # breakpoint()

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
    #background.show()

    # Merge the images
    image = image.convert("RGBA")
    image = Image.alpha_composite(image, background)
    #image = Image.blend(image, background, 0.5)
    #image.show()

    # Add captcha text to the image
    for j, c in enumerate(captcha_text):
        # Incline the digit randomly
        angle = random.randint(-20, 20)
        digit = Image.new("RGBA", (50, 50), color=(255, 255, 255, 0))
        digit_draw = ImageDraw.Draw(digit)
        #digit_draw.text(
        #    (0, 0), c, font=random.choice([font1, font2, font3]), fill=(255, 29, 29, 255)
        #)
        digit_draw.text((0, 0), c, font=font3, fill=(255, 29, 29, 255)
        )
        digit = digit.rotate(angle, expand=True)
        image.paste(digit, (30 + j * 30, 10), digit)

    # Save the image
    image.save(os.path.join(output_folder, "{}.png".format(captcha_text)))
