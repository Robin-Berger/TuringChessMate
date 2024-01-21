import random

WHITE = (255, 255, 255)
LTGRAY = (192, 192, 192)
LTGREY = (192, 192, 192)
GRAY = (128, 128, 128)
GREY = (128, 128, 128)
DKGRAY = (48, 48, 48)
DKGREY = (48, 48, 48)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 125, 125)
GREEN = (0,255,0)

# Different types of brown
B_cornsilk = (255, 248, 220)
B_blanchedalmond = (255, 235, 205)
B_bisque = (255, 228, 196)
B_navajowhite = (255, 222, 173)
B_wheat = (245, 222, 179)
B_burlywood = (222, 184, 135)
B_tan	= (210, 180, 140)
B_rosybrown = (188, 143, 143)
B_sandybrown = (244, 164, 96)
B_goldenrod = (218, 165, 32)
B_peru = (205, 133, 63)
B_chocolate = (210, 105, 30)
B_saddlebrown = (139, 69, 19)
B_sienna = (160, 82, 45)
B_brown = (165, 42, 42)
B_maroon = (128, 0, 0)

#random_color(50, 250, False,False,False)
def random_color2(dark, bright, red, green, blue):
    min_c, max_c = dark, bright
    if red:
        red_c = max_c
    else:
        red_c = random.randint(min_c, max_c)
    if green:
        green_c = max_c
    else:
        green_c = random.randint(min_c, max_c)
    if blue:
        blue_c = max_c
    else:
        blue_c = random.randint(min_c, max_c)
    return red_c, green_c, blue_c


def random_color(c_min, c_max):
    red_c = random.randint(c_min, c_max)
    green_c = random.randint(c_min, c_max)
    blue_c = random.randint(c_min, c_max)
    return red_c, green_c, blue_c

#chatGPT voorstel
def random_color3(dark, bright, red=False, green=False, blue=False):
    min_c, max_c = dark, bright
    red_c = max_c if red else random.randint(min_c, max_c)
    green_c = max_c if green else random.randint(min_c, max_c)
    blue_c = max_c if blue else random.randint(min_c, max_c)
    return red_c, green_c, blue_c

#random_color2(30, 34,139,34)
def random_color2(w, red=120, green=120, blue=120):
    red_c = random.randint(red-w, red+w)
    green_c = random.randint(red-w, red+w)
    blue_c = random.randint(red-w, red+w)
    return red_c, green_c, blue_c