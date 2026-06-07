import colorsys

def rgb_to_hue(r, g, b):
    """Convert RGB (0-1) to MIDI hue 0-127"""
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    print (h, s, v)
    return float(h)
