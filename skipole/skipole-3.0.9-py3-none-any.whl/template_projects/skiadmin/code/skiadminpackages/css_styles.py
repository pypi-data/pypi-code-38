


"""This module consists of functions which create the
admin css styles
"""

import copy, colorsys


def get_colours(R, G, B):

    colours = {}

    w3_theme_background_color = int_hex(R, G, B)

    colours["w3_theme_background_color" ] = w3_theme_background_color
    colours["w3_theme_color" ] = textcolor(R, G, B)

    w3_text_theme_color, r, g, b = other_hue_change(R, G, B)
    colours["w3_text_theme_color"]  = w3_text_theme_color
    colours["w3_border_theme_color"] = colours["w3_text_theme_color"]

    w3_theme_light_background_color, r, g, b = light_color(R, G, B)
    colours["w3_theme_light_background_color" ] = w3_theme_light_background_color
    colours["w3_theme_light_color"] = textcolor(r, g, b)

    w3_hover_theme_hover_background_color, r, g, b = hue_change(R, G, B)
    colours["w3_hover_theme_hover_background_color"] = w3_hover_theme_hover_background_color
    colours["w3_hover_theme_hover_color"] = textcolor(r, g, b)
    colours["w3_hover_text_theme_color"], r, g, b = hue_change(r, g, b)
    colours["w3_hover_border_theme_hover_color"] = colours["w3_hover_text_theme_color"]
 

    w3_theme_dark_background_color, r, g, b = dark_color(R, G, B)
    colours["w3_theme_dark_background_color" ] = w3_theme_dark_background_color
    colours["w3_theme_dark_color"] = textcolor(r,g,b)


    w3_theme_action_background_color, r, g, b = dark_color(r, g, b)
    colours["w3_theme_action_background_color" ] = w3_theme_action_background_color
    colours["w3_theme_action_color"] = textcolor(r,g,b)

    w3_theme_l1_background_color, r, g, b = lighter_color(R, G, B)
    colours["w3_theme_l1_background_color" ] = w3_theme_l1_background_color
    colours["w3_theme_l1_color"] = textcolor(r, g, b)

    w3_theme_l2_background_color, r, g, b = lighter_color(r, g, b)
    colours["w3_theme_l2_background_color" ] = w3_theme_l2_background_color
    colours["w3_theme_l2_color"] = textcolor(r, g, b)

    w3_theme_l3_background_color, r, g, b = lighter_color(r, g, b)
    colours["w3_theme_l3_background_color" ] = w3_theme_l3_background_color
    colours["w3_theme_l3_color"] = textcolor(r, g, b)

    w3_theme_l4_background_color, r, g, b = lighter_color(r, g, b)
    colours["w3_theme_l4_background_color" ] = w3_theme_l4_background_color
    colours["w3_theme_l4_color"] = textcolor(r, g, b)

    w3_theme_l5_background_color, r, g, b = lighter_color(r, g, b)
    colours["w3_theme_l5_background_color" ] = w3_theme_l5_background_color
    colours["w3_theme_l5_color"] = textcolor(r, g, b)

    w3_theme_d1_background_color, r, g, b = darker_color(R, G, B)
    colours["w3_theme_d1_background_color" ] = w3_theme_d1_background_color
    colours["w3_theme_d1_color"] = textcolor(r, g, b)

    w3_theme_d2_background_color, r, g, b = darker_color(r, g, b)
    colours["w3_theme_d2_background_color" ] = w3_theme_d2_background_color
    colours["w3_theme_d2_color"] = textcolor(r, g, b)

    w3_theme_d3_background_color, r, g, b = darker_color(r, g, b)
    colours["w3_theme_d3_background_color" ] = w3_theme_d3_background_color
    colours["w3_theme_d3_color"] = textcolor(r, g, b)

    w3_theme_d4_background_color, r, g, b = darker_color(r, g, b)
    colours["w3_theme_d4_background_color" ] = w3_theme_d4_background_color
    colours["w3_theme_d4_color"] = textcolor(r, g, b)

    w3_theme_d5_background_color, r, g, b = darker_color(r, g, b)
    colours["w3_theme_d5_background_color" ] = w3_theme_d5_background_color
    colours["w3_theme_d5_color"] = textcolor(r, g, b)

    return colours




def add_styles(style1, style2):
    """merges a copy of style2 into style1 - style1 changed in-place, returns None"""
    c_style2 = copy.deepcopy(style2)
    for key in c_style2:
        style1[key] = c_style2[key]

def textcolor(r, g, b):
    "Given a background color, suggests a textcolor and returns text-hexstring"
    if r>250 and g>250 and b>250:
        # If background is white, use black text
        return '#000000'
    elif r<100 and g<100 and b>150:
        # if background is blue, use white text
        return '#ffffff'
    elif r<150 and g<150 and b>250:
        # if background is blue, use white text
        return '#ffffff'

    h,s,l = rgb_hsl(r, g, b)
    # get a contrasting tone for text
    if l>0.8:
        # for light background, make text dark, but same hue
        opl = 0.2
    elif l>0.5:
        # for lightish background, make text black
        return '#000000'
    elif l>0.2:
        # for darkish background, make text white
        return '#ffffff'
    else:
        # for dark background, have lighter text
        opl = 0.8
    # Choose same saturation
    new_r, new_g, new_b = hsl_rgb(h, s, opl)
    return int_hex(new_r, new_g, new_b) 

def light_color(r, g, b):
    "Given a background color, suggests a lighter background color and returns (hexstring, r,g,b)"
    h,s,l = rgb_hsl(r, g, b)
    new_l = (l + 1.0)/2.0
    r, g, b = hsl_rgb(h, s, new_l)
    return int_hex(r,g,b), r, g, b

def lighter_color(r, g, b):
    "Given a background color, suggests a lighter background color and returns (hexstring, r,g,b)"
    h,s,l = rgb_hsl(r, g, b)
    new_l = (l + 2.0)/3.0
    r, g, b = hsl_rgb(h, s, new_l)
    return int_hex(r,g,b), r, g, b

def dark_color(r, g, b):
    "Given a background color, suggests a darker background color and returns (hexstring, r,g,b)"
    h,s,l = rgb_hsl(r, g, b)
    new_l = l/2.0
    r, g, b = hsl_rgb(h, s, new_l)
    return int_hex(r,g,b), r, g, b

def darker_color(r, g, b):
    "Given a background color, suggests a darker background color and returns (hexstring, r,g,b)"
    h,s,l = rgb_hsl(r, g, b)
    new_l = 2.0*l/3.0
    r, g, b = hsl_rgb(h, s, new_l)
    return int_hex(r,g,b), r, g, b

def hue_change(r, g, b):
    "Given a background color, suggests a hue change color, and l of 0.5 and returns (hexstring, r,g,b)"
    h,s,l = rgb_hsl(r, g, b)
    new_h = h+0.2
    if new_h>1:
        new_h = new_h - 1
    r, g, b = hsl_rgb(new_h, s, 0.5)
    return int_hex(r,g,b), r, g, b

def other_hue_change(r, g, b):
    "Given a background color, suggests a hue change color, and l of 0.5 and returns (hexstring, r,g,b)"
    h,s,l = rgb_hsl(r, g, b)
    new_h = h-0.2
    if new_h<0:
        new_h = new_h + 1
    r, g, b = hsl_rgb(new_h, s, 0.5)
    return int_hex(r,g,b), r, g, b


def int_hex(r, g, b):
    "converts rgb to a hex string"
    hex_value = '#'
    hexr = hex(r)[2:]
    if len(hexr) == 1:
        hex_value += "0"+hexr
    else:
        hex_value += hexr
    hexg = hex(g)[2:]
    if len(hexg) == 1:
        hex_value += "0"+hexg
    else:
        hex_value += hexg
    hexb = hex(b)[2:]
    if len(hexb) == 1:
        hex_value += "0"+hexb
    else:
        hex_value += hexb
    return hex_value

def hex_int(hexstring):
    "converts #hexdigits to r,g,b integer colours"
    if not hexstring:
        return 0,0,0
    hexstring = hexstring.strip('#')
    r = int(hexstring[0:2], base=16)
    g = int(hexstring[2:4], base=16)
    b = int(hexstring[4:6], base=16)
    return r, g, b

def rgb_hsl(r, g, b):  # rgb 0 to 255
    "converts rgb values to hsl"
    h,l,s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    return h,s,l

def hsl_rgb(h, s, l):  # hsl from 0 to 1
    "converts hsl values to rgb"
    r,g,b = colorsys.hls_to_rgb(h, l, s)
    r = round(255 * r)
    g = round(255 * g)
    b = round(255 * b)
    if r>255: r=255
    if g>255: g=255
    if b>255: b=255
    return r,g,b


