import argparse
import pywal
import os
import sys
import re
import json
import logging
import ctypes
import select
import colorsys

logging.basicConfig(level=logging.INFO)
logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s (%(levelname)s) - %(message)s'))

HOME_PATH = os.environ['HOME']
ORIGIN_VESKTOP_THEME_PATH = os.path.join(HOME_PATH, ".config/vesktop/themes")
IS_STDIN = select.select([sys.stdin], [], [], 0.0)[0]
colors = {}
DEFAULT_THEME = """
/**
 * @name Walcord Default Theme
 * @description Hello source code reader! This is a default theme generated by Walcord.
 * @author Danrus110 & danihek
 * @version 1.1.0
 * @website https://github.com/Danrus1100/walcord
**/

@import url(https://mwittrien.github.io/BetterDiscordAddons/Themes/DiscordRecolor/DiscordRecolor.css);

:root {
	--settingsicons:		0;
	--font:				"gg sans", "Noto Sans";												
}

.theme-dark {
	/* Accent Colors */
	--accentcolor: KEY(A).rgb_values;
	--accentcolor2: KEY(A).rgb_values;
	--linkcolor: KEY(BR).rgb_values;
	--mentioncolor: KEY(A).rgb_values;
	--successcolor: 59,165,92;
	--warningcolor: 250,166,26;
	--dangercolor: 237,66,69;

	/* Text Colors */
	--textbrightest: KEY(T).rgb_values;
	--textbrighter: KEY(T).rgb_values;
	--textbright: KEY(T).rgb_values;
	--textdark: KEY(T).rgb_values;
	--textdarker: KEY(T).rgb_values;
	--textdarkest: KEY(13).rgb_values;

	/* Background Colors */
	--backgroundaccent: KEY(B, 0.6).rgb_values;
	--backgroundprimary: KEY(B).rgb_values;
	--backgroundsecondary: KEY(B).rgb_values;
	--backgroundsecondaryalt: KEY(B).rgb_values;
	--backgroundtertiary: rgba(0, 0, 0, 0.05);
	--backgroundfloating: hsla(220, 20%, 40%, 0.2);
}

.theme-light {
	/* Accent Colors */
	--accentcolor: KEY(8).rgb_values;
	--accentcolor2: KEY(8).rgb_values;
	--linkcolor: KEY(A).rgb_values;
	--mentioncolor: KEY(B).rgb_values;
	--successcolor: 59,165,92;
	--warningcolor: 250,166,26;
	--dangercolor: 237,66,69;

	/* Text Colors */
	--textbrightest: KEY(T).rgb_values;
	--textbrighter: KEY(T).rgb_values;
	--textbright: KEY(T).rgb_values;
	--textdark: KEY(T).rgb_values;
	--textdarker: KEY(T).rgb_values;
	--textdarkest: KEY(13).rgb_values;

	/* Background Colors */
	--backgroundaccent: KEY(BR, 0.6).rgb_values;
	--backgroundprimary: KEY(BR).rgb_values;
	--backgroundsecondary: KEY(BR).rgb_values;
	--backgroundsecondaryalt: KEY(BR).rgb_values;
	--backgroundtertiary: rgba(0, 0, 0, 0.05);
	--backgroundfloating: hsla(220, 20%, 40%, 0.2);
}
"""

def get_colors_pywal(image_path: str) -> dict:
    """
    Returns a dictionary of colors generated from the given image path.

    :param image_path: The path to the image to generate colors from.
    :type image_path: str
    :return: A dictionary of colors in the format of pywal.
    :rtype: dict
    """
    logging.info(f"(walcord) getting colors from image: {image_path}")
    return pywal.colors.get(image_path)

def get_colors_json(path:str = os.path.join(HOME_PATH, ".cache/wal/colors.json")) -> dict:
    """
    Returns a dictionary of colors from the pywal json file.

    :return: A dictionary of colors in the format of pywal.
    :rtype: dict
    """
    logging.info(f"(walcord) getting colors from json ({path})...")
    if not path.endswith('.json'):
        logging.error(f"(walcord) Error: {path} is not a json file.")
        sys.exit(-1)
    elif not os.path.exists(path):
        logging.error(f"(walcord) Error: {path} not found. Maybe you should run 'wal' first?")
        sys.exit(-1)

    with open(path) as f:
        return json.load(f)

def map_colors(colors: dict) -> dict:
    """
    Maps the given colors to list.

    :param colors: The colors to map to the theme file.
    :type colors: dict
    """
    return {
        "wallpaper": colors["wallpaper"],
        "background": colors["special"]["background"],
        "foreground": colors["special"]["foreground"],
        "0": colors["colors"]["color0"],
        "1": colors["colors"]["color1"],
        "2": colors["colors"]["color2"],
        "3": colors["colors"]["color3"],
        "4": colors["colors"]["color4"],
        "5": colors["colors"]["color5"],
        "6": colors["colors"]["color6"],
        "7": colors["colors"]["color7"],
        "8": colors["colors"]["color8"],
        "9": colors["colors"]["color9"],
        "10": colors["colors"]["color10"],
        "11": colors["colors"]["color11"],
        "12": colors["colors"]["color12"],
        "13": colors["colors"]["color13"],
        "14": colors["colors"]["color14"],
        "15": colors["colors"]["color15"],

        # special colors
        "border": colors["colors"]["color2"],
        "text": colors["colors"]["color15"],
        "accent": colors["colors"]["color13"],

        # short names
        "b": colors["special"]["background"], 
        "f": colors["special"]["foreground"],
        "br": colors["colors"]["color2"],
        "t": colors["colors"]["color15"],
        "a": colors["colors"]["color13"],
        "w": colors["wallpaper"]

    }

def hex_to_rgb_map(colors: dict) -> dict:
    """
    Maps the hex colors to rgb colors.

    :param color: The colors to map to rgb.
    :type color: dict
    :return: A list of colors mapped to rgb.
    :rtype: dict
    """
    returned = {}
    for color in colors:
        try:
            returned[color] = tuple(int(colors[color].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            if color == "wallpaper" or color == "w":
                returned[color] = colors[color] # wallpaper path (expecting string)
                continue
            logging.warning(f"Param '{color}' is not a valid hex color. Skipping...")
            continue
    return returned

def rgb_to_hls(color: tuple) -> tuple:
    """
    Converts the given rgb color to hls.

    :param color: The color to convert to hls.
    :type color: tuple
    :return: The color converted to hls.
    :rtype: tuple
    """
    r, g, b = color
    return colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

def add_to_color_tuple(color: tuple, value: int, pos: int) -> tuple:
    color = list(color)
    color[pos] += value
    return tuple(color)

def invert_color(color: tuple) -> tuple:
    return tuple(255 - i for i in color)

def check_and_apply_second_modificator(color_tuple: tuple, scond_mod: dict) -> tuple:
    if scond_mod["type"] == "add" or scond_mod["type"] == "sub":
        color_tuple = add_to_color_tuple(color_tuple, scond_mod["mod"], scond_mod["pos"])
    elif scond_mod["type"] == "invert":
        color_tuple = invert_color(color_tuple)
    return color_tuple

def return_rgba_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"rgba({color_tuple[0]},{color_tuple[1]},{color_tuple[2]},{opacity})"

def return_rgb_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"rgb({color_tuple[0]},{color_tuple[1]},{color_tuple[2]})"

def return_values_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"{color_tuple[0]},{color_tuple[1]},{color_tuple[2]},{opacity}"

def return_values_without_opacity_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"{color_tuple[0]},{color_tuple[1]},{color_tuple[2]}"

def return_red_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"{color_tuple[0]}"

def return_green_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"{color_tuple[1]}"

def return_blue_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"{color_tuple[2]}"

def return_opacity_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"{opacity}"

def return_hex_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"#{color_tuple[0]:02x}{color_tuple[1]:02x}{color_tuple[2]:02x}"

def return_hex_values_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    color_tuple = check_and_apply_second_modificator(color_tuple, scond_mod)
    return f"{color_tuple[0]:02x}{color_tuple[1]:02x}{color_tuple[2]:02x}"

def return_hsl_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}): 
    h, l, s = check_and_apply_second_modificator(rgb_to_hls(color_tuple))
    return f"hsl({h},{l},{s})"

def return_h_from_hsl_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    h, l, s = check_and_apply_second_modificator(rgb_to_hls(color_tuple))
    return f"{h}"

def return_s_from_hsl_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    h, l, s = check_and_apply_second_modificator(rgb_to_hls(color_tuple))
    return f"{s}"

def return_l_from_hsl_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    h, l, s = check_and_apply_second_modificator(rgb_to_hls(color_tuple))
    return f"{l}"

def return_hsl_values_string(color_tuple, opacity, scond_mod = {"pos": 0, "mod": 0, "type": None}):
    h, l, s = check_and_apply_second_modificator(rgb_to_hls(color_tuple))
    return f"{h},{l},{s}"

FIRST_MODIFIERS = {
    'DEFAULT': return_rgba_string,
    '.rgba': return_rgba_string,
    '.rgb': return_rgb_string,
    '.hex': return_hex_string,
    '.hsl': return_hsl_string,

    '.rgba_values': return_values_string,
    '.rgb_values': return_values_without_opacity_string,
    '.hex_values': return_hex_values_string,
    '.hsl_values': return_hsl_values_string,

    '.r': return_red_string,
    '.red': return_red_string,

    '.g': return_green_string,
    '.green': return_green_string,

    '.b': return_blue_string,
    '.blue': return_blue_string,

    '.o': return_opacity_string,
    '.opacity': return_opacity_string,

    '.h': return_h_from_hsl_string,
    '.hue': return_h_from_hsl_string,

    '.s': return_s_from_hsl_string,
    '.saturation': return_s_from_hsl_string,

    '.l': return_l_from_hsl_string,
    '.lightness': return_l_from_hsl_string
}

def add_modificator(params):
    # print(params)
    p = params.replace(" ","").replace("(", "").replace(")", "").split(",")
    if len(p) < 2 or len(p) > 2:
        raise ValueError(f"Add modificator takes 2 parameters. You gave {len(p)} parameters")
    return {"pos": int(p[0]), "mod": int(p[1]), "type": "add"}

def sub_modificator(params):
    p = params.replace(" ","").replace("(", "").replace(")", "").split(",")
    if len(p) < 2 or len(p) > 2:
        raise ValueError(f"Add modificator takes 2 parameters. You gave {len(p)} parameters")
    return {"pos": int(p[0]), "mod": -1 * int(p[1]), "type": "sub"}

def invert_modificator(params):
    if params:
        raise ValueError(f"Invert modificator takes no parameters. You gave {params}")
    return {"pos": 0, "mod": 0, "type": "invert"}


SECOND_MODIFIERS = {
    '.add': add_modificator,
    '.sub': sub_modificator,
    '.invert': invert_modificator,

    # aliases
    '.a': add_modificator,
    '.s': sub_modificator,
    '.i': invert_modificator
}



    

def remap_key(match: re.Match) -> str:
    """
    Remaps the key to the css rgba format.

    :param match: The match object to remap.
    :type match: re.Match
    """
    first_arg = match.group(1).lower()
    first_arg_values = colors.get(first_arg)
    if not first_arg_values:
        raise ValueError(f"Color '{first_arg}' not found in the colors dictionary.")
    second_arg = match.group(2) if match.group(2) else "1.0"
    try:
        second_arg = float(second_arg)
        if second_arg < 0.0:
            opacity = 1.0
            raise ValueError(f"Opacity value is not a valid: {second_arg} (it should be 0.0-1.0 or 1-100). Opacity will be set to 1.0...")
        if second_arg > 1.0 and second_arg <= 100:
            second_arg = second_arg / 100
        elif second_arg > 100:
            opacity = 1.0
            raise ValueError(f"Opacity value is not a valid: {second_arg} (it should be less than 100%). Opacity will be set to 1.0...")
        opacity = second_arg
    except Exception as e:
        opacity = 1.0
        raise ValueError(f"Opacity value is not a valid: {second_arg}. opacity will be set to 1.0")


    first_modifier = match.group(3).lower() if match.group(3) else None
    second_modifer:str = match.group(4).lower() if match.group(4) else None
    second_modifer_name: str = re.sub(r'[0-9,]', '', second_modifer.replace("(", "").replace(")", "")).replace(" ", "") if second_modifer else None
    second_modifer_raw_params = match.group(5)

    second_modifer_params = {
        "pos": 0,
        "mod": 0,
        "type": None
    }

    # print(second_modifer_name)

    if second_modifer and second_modifer_name in SECOND_MODIFIERS:
        second_modifer_params = SECOND_MODIFIERS[second_modifer_name](second_modifer_raw_params)

    if (first_arg == "wallpaper" or first_arg == "w") and (opacity != 1.0 or first_modifier):
        raise ValueError(f"You cant use opacity or modifier with wallpaper key.")
    if first_modifier and first_modifier in FIRST_MODIFIERS:
        return FIRST_MODIFIERS[first_modifier](first_arg_values, opacity, second_modifer_params)
    return FIRST_MODIFIERS['DEFAULT'](first_arg_values, opacity)

def replace_key(text: str) -> str:
    """
    Replaces the key with the rgba format.

    :param text: The text to replace the key in.
    :type text: str
    :return: The text with the key replaced.
    :rtype: str
    """
    return re.sub(r'KEY\((\w+)(?:,\s*(\d+(?:\.\d+)?))?\)(\.\w+)?(\.\w+(\(\d+(?:\.\d+)?(?:,\s*\d+(?:\.\d+)?)?\))?)?', remap_key, text, flags=re.IGNORECASE)

def check_path(path: str, file_name: str = "") -> None:
    """
    Checks if the path exists and if not creates it.

    :param path: The path to check.
    :param file_name: The name of the file to create if name dosent given.
    :type path: str
    """
    if "~" in path: path = path.replace("~", HOME_PATH)
    if not os.path.exists(path):
        logging.info(f"(walcord) Path not found: {path}")
        if "." in path[1:]:
            if len(theme_files_paths) > 1:
                logging.error(f"(walcord) Error: You can't use multiple theme files with a single output file.")
                sys.exit(-1)
            logging.info(f"(walcord) Creating file: {path}")
            try:
                with open(path, "w+") as f:
                    pass
            except IsADirectoryError:
                logging.error(f"(walcord) Path is a directory: {path}. Output path should be a file path.")
                sys.exit(-1)
        else:
            logging.info(f"(walcord) Creating directory: {path}")
            os.makedirs(path)
            if file_name != "":
                with open(os.path.join(path, file_name), "w+") as f:
                    pass
    logging.info(f"(walcord) Path checked: {path}")

theme_files_paths = []

def check_themes(theme: str) -> None:
    """
    Checks if the theme file exists and make a list of theme files.

    :param theme: The path to the theme file to check.
    :type theme: str
    """
    logging.info(f"(walcord) checking theme path: {theme}")
    if "~" in theme: theme = theme.replace("~", HOME_PATH)
    if os.path.isfile(theme): # Check if path is a file
        theme_files_paths.append(theme)
    elif os.path.isdir(theme): # Check if path is a directory
        for root, dirs, files in os.walk(theme):
            for file in files:
                theme_files_paths.append(os.path.join(root, file))
    else: # Path is not a file or directory so error
        logging.error(f"(walcord) Error: Is not an existing file or directory: {theme}")
        sys.exit(-1)
    logging.info(f"(walcord) found {len(theme_files_paths)} theme files.")

def try_replace_key_in_theme(lines: dict, filename: str, end: str = "") -> str:
    output = ""
    for n, i in enumerate(lines):
        if bool(re.search(r'KEY\([^)]*\)', i, re.IGNORECASE)):
            try:
                new_line = replace_key(i) + end
                if new_line == i + end:
                    logging.warning(f"(walcord) in line {n+1} in {filename}: KEY parse error. Maybe you wrote the wrong parameters?")
                output += new_line
            except Exception as e:
                logging.error(f"(walcord) in line {n+1} in {filename}: {e}")
        else:
            output += i + end
    
    return output

def main():
    global colors
    global VESKTOP_THEME_PATH
    global IS_STDIN

    parser = argparse.ArgumentParser(description="Create a theme file from pywal colors.")
    parser.add_argument("--image", "-i", type=str, help="The path to the image to generate colors from.", required=False)
    parser.add_argument("--theme", "-t", type=str, help="The path to the theme file to replace colors in.", required=False)
    parser.add_argument("--output", "-o", type=str, help="The path to the output file. default: ~/.config/vesktop/themes/", required=False)
    parser.add_argument("--quiet", "-q", action="store_true", help="Don't print anything.", required=False)
    parser.add_argument("--extention", "-e", type=str, help="The extention of the theme file, if you use stdin. (default: '.css')", required=False)
    parser.add_argument("--json", "-j", type=str, help="colors.json file with pywal colors", required=False)
    parser.add_argument("--stdin", "-si", action="store_true", help="Read theme from stdin.", required=False)
    #parser.add_argument("--service", "-s", type=bool, help="Work as a service.", required=False)
    parser.add_argument("--version", "-v", action="version", version="2.9.1")
    args = parser.parse_args()

    if args.quiet: logging.getLogger().setLevel(logging.ERROR)

    logging.info(f"(walcord) gettings colors...")
    if args.json:
        colors = get_colors_json(args.json)
    else:
        colors = get_colors_pywal(args.image) if args.image else get_colors_json()
    colors = hex_to_rgb_map(map_colors(colors))

    if IS_STDIN and args.stdin:
        if args.theme:
            logging.error("(walcord) Error: You can't use stdin with --theme.")
            sys.exit(-1)
        logging.info("(walcord) getting data from stdin...")
        stdin_data = sys.stdin.read().split("\n")
        theme_files_paths.append("STDIN_THEME")

    else:
        if args.theme: 
            check_themes(args.theme)
        else: 
            theme_files_paths.append("DEFAULT_THEME")

    if args.output: 
        logging.info(f"(walcord) checking output path: {args.output}")
        check_path(args.output)

    for theme_file in theme_files_paths:
        VESKTOP_THEME_PATH = ORIGIN_VESKTOP_THEME_PATH
        logging.info(f"(walcord) working on the file: {theme_file}")
        if theme_file == "DEFAULT_THEME":
            theme_lines = DEFAULT_THEME.split("\n")
            theme_file_name = "walcord.theme.css"
        elif theme_file == "STDIN_THEME":
            theme_lines = stdin_data
            theme_file_name = "stdin.walcord.theme.css"
            for i in range(len(theme_lines)):
                if "@name" in theme_lines[i]:
                    theme_file_name = theme_lines[i].split(" ")[-1].strip()
                    theme_file_name += ".css" if not args.extention else args.extention

        else:
            theme_file_name = os.path.basename(theme_file)
            theme_lines = open(theme_file, "r+").readlines()

        VESKTOP_THEME_PATH = args.output if args.output else os.path.join(VESKTOP_THEME_PATH, theme_file_name)
        if not "." in VESKTOP_THEME_PATH[1:]: VESKTOP_THEME_PATH = os.path.join(VESKTOP_THEME_PATH, theme_file_name)

        logging.info(f"(walcord) start to generate theme file...")
        for i in range(len(theme_lines)):
            if "@description" in theme_lines[i]:
                theme_lines[i] = " * @description Generated by Walcord\n"
                break
        
        theme_text = try_replace_key_in_theme(theme_lines, theme_file, "\n" if not args.theme else "")
            
        logging.info(f"(walcord) writing theme file to: {VESKTOP_THEME_PATH}")
        with open(VESKTOP_THEME_PATH, "w+") as file: file.write(theme_text)
        logging.info(f"(walcord) {VESKTOP_THEME_PATH} generated successfully.")
    logging.info("(walcord) DONE.")

if __name__ == "__main__":
    main()
