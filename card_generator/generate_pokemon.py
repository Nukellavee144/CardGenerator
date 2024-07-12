from io import BytesIO

import pandas as pd
import requests
from PIL import ImageDraw, Image, ImageChops
from tqdm import tqdm
import urllib.request

from config import *
from utils import xy, read_cube, get_img, text_font, title_font, wrapped_text


#
# Base
#


def compose_base(stats):
    base_img = get_img(CARD_ASSETS_DIR / 'card_bases' / 'standard.png', xy(16, 23))

    if not pd.isnull(stats.biome):
        biome_name = stats.biome.lower()
        biome_img = get_img(CARD_ASSETS_DIR / 'biomes' / f'{biome_name}.png', xy(16, 11))
        base_img.alpha_composite(biome_img, xy(0, 2))
    else:
        biome_img = get_img(CARD_ASSETS_DIR / 'biomes' / 'unknown.png', xy(16, 11))
        base_img.alpha_composite(biome_img, xy(0, 2))
    return base_img


def add_frame(img, stats):
    #frame_img = get_img(CARD_ASSETS_DIR / 'frame_base.png', xy(16, 23))  
    #img.paste(frame_img, xy(0.25, 0.25), frame_img)
    
    
    frame_overlay = get_img(CARD_ASSETS_DIR / 'frame_overlays' / f'{stats.color.lower()}_frame.png', xy(16, 23))
    img.paste(frame_overlay, xy(0, 0), frame_overlay)


#
# Pictures
#

def get_pokemon_img_size(stats):
    min_size = 7
    max_size = 10
    return max_size


def converted_pokedex_number(stats, i):
    split_pokedex_number = str(stats.pokedex_number).split('-')
    if split_pokedex_number[0].isdigit():
        
        split_pokedex_number[0] = f'{int(split_pokedex_number[0]):00}' if i == 0 else f'{int(split_pokedex_number[0]):03}'
    return '-'.join(split_pokedex_number)


def get_pokemon_img(stats):
    img_size = get_pokemon_img_size(stats)
    img_name = converted_pokedex_number(stats, 0)
    try:
        pokemon_img = get_img(CARD_ASSETS_DIR / 'pokemon' / f'{img_name}.png', xy(img_size, img_size))
    except (FileNotFoundError, AttributeError):
        try:
            download_image(f'{ART_FORM_URL}/{img_name}.png', img_name)        
        except: 
            try:
                img_name = converted_pokedex_number(stats, 1)
                download_image(f'{ART_FORM_URL2}/{img_name}.png',img_name)
            except:
                return
        #response = requests.get(f'{ART_FORM_URL}/{img_name}.png')
        pokemon_img = get_img(CARD_ASSETS_DIR / 'pokemon' / f'{img_name}.png', xy(img_size, img_size))
        #pokemon_img = get_img(BytesIO(response.content), xy(img_size, img_size))
        #pokemon_img.save(CARD_ASSETS_DIR / 'pokemon' / f'{img_name}.png')
    return pokemon_img

def download_image(url, filename):
    r = requests.get(url)
    try:
        im = Image.open(BytesIO(r.content))
    except:
        raise ValueError('Couldnt find image')
    im.save(CARD_ASSETS_DIR / 'pokemon' / f'{filename}.png')

def trim_pokemon_image(img):    
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)

def add_pokemon_img(img, stats):
    pokemon_img = get_pokemon_img(stats)
    if pd.isnull(pokemon_img): 
        print("Couldn't find image for ", stats.pokedex_name)
        return
    pokemon_img = trim_pokemon_image(pokemon_img)
    pokemon_img_pos = xy((16 - pokemon_img.width / 64) / 2, (15 - pokemon_img.height / 64) / 2)
    img.paste(pokemon_img, pokemon_img_pos, pokemon_img)


#
# Bases
#

def add_all_bases(img, stats):
    add_stats_bases(img, stats)


def add_stats_bases(img, stats):
    if not pd.isnull(stats.cost):
        health_base_img = get_img(CARD_ASSETS_DIR / 'stats_bases' / 'health.png', xy(2, 2))
        img.paste(health_base_img, xy(13.75, 0.25), health_base_img)

    if not pd.isnull(stats.attack):
        power_base_img = get_img(CARD_ASSETS_DIR / 'stats_bases' / 'power.png', xy(1.75, 1.75))
        img.paste(power_base_img, xy(14, 21.1), power_base_img)

    if not pd.isnull(stats.health):
        health_base_img = get_img(CARD_ASSETS_DIR / 'stats_bases' / 'power.png', xy(1.75, 1.75))
        img.paste(health_base_img, xy(12, 21.1), health_base_img)


#
# Icons
#

def add_all_icons(img, stats):
    add_type_icons(img, stats)


def get_types(stats):
    return [type_ for type_ in (stats.type_1, stats.type_2) if not pd.isnull(type_)]


def add_type_icons(img, stats):
    types = get_types(stats)
    for i, type_ in enumerate(types):
        type_img = get_img(CARD_ASSETS_DIR / 'types' / f'{type_}.png', xy(1, 1))
        type_pos = xy(1.75 + i * 1.2, 21.9)
        img.paste(type_img, type_pos, type_img)

#
# Finishing Touches
#

def add_text(img, stats):
    d = ImageDraw.Draw(img)
    types = get_types(stats)

    # Pokémon Name
    name_pos = xy(6.5, 1.5 - (0.5 if not pd.isnull(stats.tags) else 0))
    name_font_size = text_font(44) if pd.isnull(stats.tags) else text_font(36)
    d.text(name_pos, stats.pokedex_name, fill=DARK_COLOUR, font=name_font_size, anchor='mm')
  
    # Pokemon Tags
    if not pd.isnull(stats.tags):
        d.text(xy(6.5, 2), stats.tags, fill=DARK_COLOUR, font=text_font(20), anchor="mm")


    # Pokémon Stats
    if not pd.isnull(stats.cost):
        wrapped_text(d, str(int(stats.cost)), title_font(40), boundaries=(4, 4), xy=xy(14.8, 1.2), fill=DARK_COLOUR, alignment="center", anchor='mm')
    if not pd.isnull(stats.attack):
        wrapped_text(d, str(int(stats.attack)), title_font(40), boundaries=(4, 4), xy=xy(14.9, 22), fill=DARK_COLOUR, alignment="center", anchor='mm')
    if not pd.isnull(stats.health):
        wrapped_text(d, str(int(stats.health)), title_font(40), boundaries=(4, 4), xy=xy(12.9, 22), fill=DARK_COLOUR, alignment="center", anchor='mm')

    SetUpTextForFormats(d, GetFormat(stats), stats)

    if not pd.isnull(stats.pokedex_number):
        wrapped_text(d, str(stats.pokedex_number), text_font(20), boundaries=(2,1), xy=xy(.3,22.7), fill=DARK_COLOUR, alignment="left", anchor="ls")

def GetFormat(stats):
    format = 0

    hasAbilityDesc          = not pd.isnull(stats.ability)
    hasAbilityName          = not pd.isnull(stats.ability_name)    
    hasModeOne              = not pd.isnull(stats.mode_1_ability)
    hasModeOneName          = not pd.isnull(stats.mode_1_name)
    hasModeTwo              = not pd.isnull(stats.mode_2_ability)
    hasModeTwoName          = not pd.isnull(stats.mode_2_name)
    hasModeThree            = not pd.isnull(stats.mode_3_ability)
    hasModeThreeName        = not pd.isnull(stats.mode_3_name) 

    hasNoModes              = not hasModeOne and not hasModeTwo and not hasModeThree
    hasTwoUnnamedModes      = hasModeOne and not hasModeOneName and hasModeTwo and not hasModeTwoName and not hasModeThree
    hasTwoNamedModes        = hasModeOne and hasModeOneName and hasModeTwo and hasModeTwoName and not hasModeThree
    hasThreeUnnamedModes    = hasModeOne and not hasModeOneName and hasModeTwo and not hasModeTwoName and hasModeThree and not hasModeThreeName
    hasThreeNamedModes      = hasModeOne and hasModeOneName and hasModeTwo and hasModeTwoName and hasModeThree and hasModeThreeName

    #Setup Different Formats for Cards
    #0: Has an ability description
    #1: Has an ability name, and ability description
    #2: Has an ability name, ability description, and two modes.
    #3: Has an ability name, ability description, two mode names, and two modes.
    #4: Has an ability name, ability description, and three modes. 
    #5: Has an ability name, ability description, three modes, and three mode names.
    #6: Has an ability description, and two modes. 
    #7: Has an ability description, two modes, and two mode names. 
    #8: Has an ability description, and three modes.
    #9: Has an ability description, three modes, and three mode names. 
    #10: Has only ability name
    if hasAbilityDesc: format = 0
    if hasAbilityName and hasAbilityDesc: format = 1
    if hasAbilityName and hasAbilityDesc and hasTwoUnnamedModes: format = 2
    if hasAbilityName and hasAbilityDesc and hasTwoNamedModes: format = 3
    if hasAbilityName and hasAbilityDesc and hasThreeUnnamedModes: format = 4
    if hasAbilityName and hasAbilityDesc and hasThreeNamedModes: format = 5
    if not hasAbilityName and hasAbilityDesc and hasTwoUnnamedModes: format = 6
    if not hasAbilityName and hasAbilityDesc and hasTwoNamedModes: format = 7
    if not hasAbilityName and hasAbilityDesc and hasThreeUnnamedModes: format = 8
    if not hasAbilityName and hasAbilityDesc and hasThreeNamedModes: format = 9
    if hasAbilityName and not hasAbilityDesc: format = 10
    return format



def SetUpTextForFormats(d, format, stats):
    name_size = 32
    text_size = 30
    mode_name_size = 27
    mode_text_size = 25

    if format == 0:
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,8), xy=(xy(8, 17.5)), alignment="center", anchor='mm')
    if format == 1:
        if not pd.isnull(stats.ability_name):
            text = wrapped_text(d, stats.ability_name, title_font(name_size), fill=DARK_COLOUR, boundaries=(14, 2),  xy=xy(8, 13), alignment="center", anchor='ma')
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,6), xy=(xy(8, 15)), alignment="center", anchor='ma')
    if format == 2:
        if not pd.isnull(stats.ability_name):
            text = wrapped_text(d, stats.ability_name, title_font(name_size), fill=DARK_COLOUR, boundaries=(14, 2),  xy=xy(8, 13), alignment="center", anchor='ma')
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,2), xy=(xy(8, 15.5)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,2), xy = (xy(8, 18.5)), alignment="center", anchor="mm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,2), xy = (xy(8, 20.5)), alignment="center", anchor="mm")
    if format == 3:
        if not pd.isnull(stats.ability_name):
            text = wrapped_text(d, stats.ability_name, title_font(name_size), fill=DARK_COLOUR, boundaries=(14, 2),  xy=xy(8, 13), alignment="center", anchor='ma')
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,2), xy=(xy(8, 15.125)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_name):
            wrapped_text(d, stats.mode_1_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 18.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 18.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_name):
            wrapped_text(d, stats.mode_2_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 20.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 20.5)), alignment="left", anchor="lm")
    if format == 4:
        if not pd.isnull(stats.ability_name):
            text = wrapped_text(d, stats.ability_name, title_font(name_size), fill=DARK_COLOUR, boundaries=(14, 1.5),  xy=xy(8, 13), alignment="center", anchor='ma')
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,1.5), xy=(xy(8, 14.5)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,1.5), xy = (xy(8, 17.25)), alignment="center", anchor="mm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,1.5), xy = (xy(8, 19)), alignment="center", anchor="mm")
        if not pd.isnull(stats.mode_3_ability):
            wrapped_text(d, stats.mode_3_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,1.5), xy = (xy(8, 20.75)), alignment="center", anchor="mm")
    if format == 5:
        if not pd.isnull(stats.ability_name):
            text = wrapped_text(d, stats.ability_name, title_font(name_size), fill=DARK_COLOUR, boundaries=(14, 1.5),  xy=xy(8, 13), alignment="center", anchor='ma')
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,1.1875), xy=(xy(8, 14.25)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_name):
            wrapped_text(d, stats.mode_1_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 16.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 16.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_name):
            wrapped_text(d, stats.mode_2_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 18.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 18.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_3_name):
            wrapped_text(d, stats.mode_3_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 20.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_3_ability):
            wrapped_text(d, stats.mode_3_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 20.5)), alignment="left", anchor="lm")
    if format == 6:
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,2), xy=(xy(8, 13)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,3), xy = (xy(8, 16.5)), alignment="center", anchor="mm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,3), xy = (xy(8, 19.5)), alignment="center", anchor="mm")
    if format == 7:
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,2.5), xy=(xy(8, 14)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_name):
            wrapped_text(d, stats.mode_1_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2.5), xy = (xy(1, 17)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2.5), xy = (xy(6, 17)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_name):
            wrapped_text(d, stats.mode_2_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2.5), xy = (xy(1, 20)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2.5), xy = (xy(6, 20)), alignment="left", anchor="lm")
    if format == 8:
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,2), xy=(xy(8, 12.5)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,2), xy = (xy(8, 15.75)), alignment="center", anchor="mm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,2), xy = (xy(8, 18)), alignment="center", anchor="mm")
        if not pd.isnull(stats.mode_3_ability):
            wrapped_text(d, stats.mode_3_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(14,2), xy = (xy(8, 20.25)), alignment="center", anchor="mm")
    if format == 9:
        if not pd.isnull(stats.ability):       
            wrapped_text(d, stats.ability, text_font(text_size), fill=DARK_COLOUR, boundaries=(14,2), xy=(xy(8, 12.5)), alignment="center", anchor='ma')
        if not pd.isnull(stats.mode_1_name):
            wrapped_text(d, stats.mode_1_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 15.75)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_1_ability):
            wrapped_text(d, stats.mode_1_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 15.75)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_name):
            wrapped_text(d, stats.mode_2_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 18)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_2_ability):
            wrapped_text(d, stats.mode_2_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 18)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_3_name):
            wrapped_text(d, stats.mode_3_name, title_font(mode_name_size), fill=DARK_COLOUR, boundaries=(5,2), xy = (xy(1, 20.5)), alignment="left", anchor="lm")
        if not pd.isnull(stats.mode_3_ability):
            wrapped_text(d, stats.mode_3_ability, text_font(mode_text_size), fill=DARK_COLOUR, boundaries=(9,2), xy = (xy(6, 20.5)), alignment="left", anchor="lm")
    if format == 10:
        if not pd.isnull(stats.ability_name):       
            wrapped_text(d, stats.ability_name, title_font(name_size), fill=DARK_COLOUR, boundaries=(14,8), xy=(xy(8, 17.5)), alignment="center", anchor='mm')
    return

#
# Entry
#


def run(overwrite=False):
    print('Generating card fronts:')
    CARD_FRONTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube()
    for i, stats in tqdm(df.iterrows(), total=df.shape[0]):
        output_path = CARD_FRONTS_OUTPUT_DIR / f'{i}_{stats.pokedex_name.lower()}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = compose_base(stats)

        # img = Image.new('RGBA', xy(16, 28))
        add_frame(img, stats)
        add_pokemon_img(img, stats)

        add_all_bases(img, stats)

        add_all_icons(img, stats)

        add_text(img, stats)
        # add_move(img, stats)
        # add_emblem(img)

        # base_img.paste(img, xy(0, 0), img)
        img.save(output_path)


if __name__ == '__main__':
    run(overwrite=True)