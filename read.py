import csv
import re

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

    import ipdb
    ipdb.set_trace()

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

with open('local_export_01_03.csv', 'rt', encoding='UTF-8') as f, open('export_local_03_01.csv', 'w') as n:
    reader = csv.DictReader(f, delimiter=',')
    writer = csv.DictWriter(n, reader.fieldnames, delimiter=',', quoting=csv.QUOTE_ALL)
    writer.writeheader()

    for row in reader:
            
        #print_row(row['additional_attributes'])

        # Can;t use a semicolon either as contains html with inline styles
        row['additional_attributes'] = '|'.join(print_row(row['additional_attributes']))

        #split the standard fields
        row['categories'] = '|'.join(row['categories'].split(','))

        #additional images delimter must be comma
        row['additional_images'] = '|'.join(row['additional_images'].split(','))
        row['additional_image_labels'] = '|'.join(row['additional_image_labels'].split(','))
        writer.writerow(row)
