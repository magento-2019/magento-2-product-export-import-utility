import csv
import re
from bs4 import BeautifulSoup as Soup

MAIN_ATTRIBUTES = [
    'ammunition_model', 'ammunition_use', 'ammunition_velocity', 'barrel_length', 'brand', 'bullet_brand', 'bullet_calibre', 'bullet_diameter', 'bullet_grain', 'bullet_model', 'bullet_style', 'burn_rate', 'calibre_aka', 'calibre_conversion', 'capacity', 'carbohydrate', 'cartridge_calibre', 'cartridge_case_material', 'color', 'condition', 'configurable_additional_info', 'cost', 'die_material', 'die_type', 'display_weight', 'ebizmarts_mark_visited', 'end_slider_date_product', 'energy', 'eyewear_material', 'firearm_action_type', 'firearm_barrel_end_type', 'firearm_barrel_twist_length', 'firearm_barrel_type', 'firearm_cartridge_capacity', 'firearm_colour', 'firearm_frame_material', 'firearm_grip_material', 'firearm_height', 'firearm_length', 'firearm_safety', 'firearm_sight', 'firearm_size', 'firearm_stock_material', 'firearm_trigger_action', 'firearm_type', 'firearm_weight', 'firearm_width', 'flavour', 'gauge_material', 'has_tiers', 'insurance_percentage', 'is_recurring', 'key_features', 'machine_compatibility', 'magazine_base_pad_material', 'magazine_body_material', 'magazine_capacity', 'manufacturer', 'manufacturer_part_number', 'max_qty_discount', 'normally_instock', 'optional_accesories', 'package_contents', 'pellet_calibre', 'pellet_diameter', 'pellet_material', 'pellet_model', 'pellet_tip_shape', 'pellet_weight', 'primer_aps_colour', 'primer_power', 'primer_quality', 'primer_size', 'primer_style', 'primer_type', 'product_link', 'product_weight', 'propellant_cat', 'propellant_density', 'propellant_type', 'protein', 'purpose', 'quantity_restriction', 'rating', 'recommended_accesories', 'recurring_profile', 'references', 'reloading_die_calibre', 'required_accesories', 'scale_capacity', 'shipping_restriction', 'shotshell_brass_height', 'shotshell_length', 'shot_size', 'shot_weight', 'size', 'start_slider_date_product', 'sugar', 'surface_finish', 'sw_featured', 'target_colour', 'target_material', 'technical_specifications', 'videos'
]

MULTI_SELECTS = ['machine_compatibility', 'bullet_calibre', 'firearm_sight']

TABLE_ATTRIBUTES = ['package_contents', 'technical_specifications', 'calibre_conversion', 
'required_accesories', 'recommended_accesories', 'description', 'optional_accesories']

def format_additional(row):
    '''
    Takes a string of key value values split by commas
    Return string split by semi-colon
    '''

    split_up_pattern = re.compile(r'([^=]+)=([^=]+)(?:,|$)', re.X|re.M)
    
    matches = split_up_pattern.findall(row)

    formatted_list = []
    for match in matches:
        # make a list from the tuples
        formatted_list.append('='.join(match))

    return formatted_list

def print_row(row):
    # Start of the string or our ,WORD= pattern.
    rgx_spans = re.compile(r'(\A|,)\w+=')

    # Get the start-end positions of all matches.
    spans = [m.span() for m in rgx_spans.finditer(row)]

    formatted_list = []

    # Use those positions to break up the string into parsable chunks.
    for i, pos1 in enumerate(spans):
        try:
            pos2 = spans[i + 1]
        except IndexError:
            pos2 = (None, None)

        start = pos1[0]
        end = pos2[0]
        key, val = row[start:end].lstrip(',').split('=', 1)

        formatted_list.append(key + '=' + val)

    return formatted_list

def format_value(value):
    return '|'.join(value.split(','))

def merge_rows(row):
    merged_content = []
    for key, value in row.items():
        if key in TABLE_ATTRIBUTES:
            value = clean_table(value)
        if key in MAIN_ATTRIBUTES and value:
            if key == 'bullet_diameter':
                # Remove the initial 0 created from excel/calc
                value = value[1:]
                if value == '.4':
                    value = '.400'
            if key in MULTI_SELECTS:
                value = format_value(value)
            merged_content.append(key + '=' + value)
    #import ipdb; ipdb.set_trace()
    return merged_content

def clean_table(string):
    soup = Soup(string, "html.parser")
    if soup.find('table'):
        try:
            #import ipdb; ipdb.set_trace()
            for occurance in soup.find_all('table'):
                del occurance['style']
        except KeyError:
            pass
    return str(soup)

with open('newest_export.csv', 'rt', encoding='UTF-8') as f, open('newest_import.csv', 'w') as n:
    reader = csv.DictReader(f, delimiter=',')
    writer = csv.DictWriter(n, reader.fieldnames, delimiter=',', quoting=csv.QUOTE_ALL)
    writer.writeheader()

    for row in reader:

        # Can't use a semicolon either as contains html with inline styles
        row['additional_attributes'] = '|'.join(merge_rows(row))

        for key in TABLE_ATTRIBUTES:
            row[key] = clean_table(row[key])

        #split the standard fields
        row['categories'] = '|'.join(row['categories'].split(','))

        #additional images delimter must be comma
        row['additional_images'] = '|'.join(row['additional_images'].split(','))
        row['additional_image_labels'] = '|'.join(row['additional_image_labels'].split(','))

        writer.writerow(row)
