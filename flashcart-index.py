"""
Generate flashcart index file

Run with:
    python flashcart-index.py <flashcart_directory_path>

Follow this directory structure:

    - Action
    - - Hopper.hex	        # game file
    - - Hopper.png	        # game screen file
    - - Lasers.hex
    - - Lasers.png
    - Adventure
    - - Arena.hex
    - - Arena.png
    - Categories		# category screens directory
    - - Action.png 	        # category screen file
    - - Adventure.png 		# category screen file
    - arduboy_loader.png 	# title screen
    - flashcart-image.bin 	# flash cart image
    - flashcart-index.csv	# flash card index directory needed to build image

"""
import os
import sys
import csv


CATEGORY_SCREEN_DIR = 'category-screens'


def main(flashcart_path):
    rows = []

    categories = [c for c in os.listdir(flashcart_path) if os.path.isdir(os.path.join(flashcart_path, c)) and c != CATEGORY_SCREEN_DIR ]
    categories.sort()

    rows.append(['List', 'Discription', 'Title screen', 'Hex file', 'Data file', 'Save file'])
    rows.append([0, 'Bootloader', 'arduboy_loader.png', None, None, None])

    for idx, category in enumerate(categories):
        category_num = idx + 1
        files = (list(set(filter(lambda x: x != '.DS_Store',
            map(lambda x: x.replace('.png', '').replace('.hex', ''),
            os.listdir(os.path.join(flashcart_path, category)))))))
        files.sort()

        category_screen = os.path.join(CATEGORY_SCREEN_DIR, "{}.png".format(category))
        rows.append([category_num, category, category_screen, None, None, None])

        for f in files:
            file_path = os.path.join(category, "{}.hex".format(f))
            img_file_path = os.path.join(category, "{}.png".format(f))
            rows.append([category_num, f, img_file_path, file_path, None, None])

    with open(os.path.join(flashcart_path, 'flashcart-index.csv'), 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    flashcart_path = sys.argv[1]
    if flashcart_path:
        main(flashcart_path)
    else:
        print('Missing flashcart path: python flashcart-index.py <flashcart_directory_path>')
