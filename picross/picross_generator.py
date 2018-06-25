from PIL import Image, ImageDraw, ImageFont
import numpy as np


def by_two(arr):
    for index in range(len(arr) - 1):
        yield arr[index], arr[index + 1]

def split_and_count(arr, indexes, ignore_zeros=True):
    results = []
    indexes = [0] + indexes + [len(arr)]
    for a, b in by_two(indexes):
        block = arr[a:b]
        if not (ignore_zeros and block[0] == 0):
            results.append((block[0], len(block)))
    return results

def split_indexes(arr):
    indexes = []
    for index, (a, b) in enumerate(zip(arr[:-1], arr[1:])):
        if a != b:
            indexes.append(index + 1)
    return indexes

def get_tuples(arr):
    data = []
    for line in arr:
        indexes = split_indexes(line)
        data.append(split_and_count(line, indexes))
    return data

def get_color(palette, index):
    r = palette[index * 3 + 0]
    g = palette[index * 3 + 1]
    b = palette[index * 3 + 2]
    return (r, g, b)

if __name__ == '__main__':
    BLOCK_SIZE = 32

    img = Image.open('mario.png')

    palette = bytearray(img.palette.palette)
    
    # получаем цифры по картинке
    arr = np.array(img)
    horizontal_data = get_tuples(arr)
    vertical_data = get_tuples(arr.T)

    # находим самый длинный блок с цифрами
    horizontal_blocks = 0
    for item in horizontal_data:
        horizontal_blocks = max(len(item), horizontal_blocks)
    vertical_blocks = 0
    for item in vertical_data:
        vertical_blocks = max(len(item), vertical_blocks)

    # расчитываем размер новой картинки
    nimage_width = BLOCK_SIZE * img.size[0] + horizontal_blocks * BLOCK_SIZE
    nimage_height = BLOCK_SIZE * img.size[1] + vertical_blocks * BLOCK_SIZE

    nimage = Image.new('RGBA', (nimage_width + 1, nimage_height + 1), 'white')
    draw = ImageDraw.Draw(nimage)

    # ресайзим старую картинку
    picture = img.resize((BLOCK_SIZE * img.size[0], BLOCK_SIZE * img.size[1]), Image.BILINEAR)
    # и переносим на новую
    box = (horizontal_blocks * BLOCK_SIZE, vertical_blocks * BLOCK_SIZE, nimage_width, nimage_height)
    nimage.paste(picture, box=box)
    # и рисуем рамку
    draw.rectangle(box, outline='black')

    # рисуем линии
    for x in range(horizontal_blocks * BLOCK_SIZE, nimage_width + 1, BLOCK_SIZE):
        draw.line((x, 0, x, nimage_height), 'black')
    for x in range(0, horizontal_blocks * BLOCK_SIZE, BLOCK_SIZE):
        draw.line((x, horizontal_blocks * BLOCK_SIZE, x, nimage_height), 'black')
    for y in range(vertical_blocks * BLOCK_SIZE, nimage_height + 1, BLOCK_SIZE):
        draw.line((0, y, nimage_width, y), 'black')
    for y in range(0, vertical_blocks * BLOCK_SIZE, BLOCK_SIZE):
        draw.line((horizontal_blocks * BLOCK_SIZE, y, nimage_width, y), 'black')

    # растановляем цифры
    font = ImageFont.truetype('FiraMono-Regular.ttf', size=BLOCK_SIZE - 10)
    for xindex, line in enumerate(vertical_data):
        ypos = (vertical_blocks - len(line) + 0.1) * BLOCK_SIZE
        xpos = BLOCK_SIZE * (horizontal_blocks + 0.3 + xindex)
        for color, number in line: 
            draw.text((xpos, ypos), str(number), font=font, fill=get_color(palette, color))
            ypos += BLOCK_SIZE
    for yindex, line in enumerate(horizontal_data):
        xpos = (horizontal_blocks - len(line) + 0.3) * BLOCK_SIZE
        ypos = BLOCK_SIZE * (vertical_blocks + yindex + 0.1)
        for color, number in line: 
            draw.text((xpos, ypos), str(number), font=font, fill=get_color(palette, color))
            xpos += BLOCK_SIZE

    nimage.save('mario-picross.png')