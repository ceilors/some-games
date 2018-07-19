#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json as js


def by_two(arr):
    for index in range(len(arr) - 1):
        yield arr[index], arr[index + 1]


def split_and_count(arr, indexes, one_color=False):
    results = []
    indexes = [0] + indexes + [len(arr)]
    for a, b in by_two(indexes):
        block = arr[a:b]
        if one_color:
            if block[0] == 0:
                results.append((int(block[0]), len(block)))
        else:
            if block[0] > 0:
                results.append((int(block[0]), len(block)))
    return results


def split_indexes(arr):
    indexes = []
    for index, (a, b) in enumerate(zip(arr[:-1], arr[1:])):
        if a != b:
            indexes.append(index + 1)
    return indexes


def get_tuples(arr, one_color=False):
    data = []
    for line in arr:
        indexes = split_indexes(line)
        data.append(split_and_count(line, indexes, one_color=one_color))
    return data


def get_color(palette, index):
    r = palette[index * 3 + 0]
    g = palette[index * 3 + 1]
    b = palette[index * 3 + 2]
    return (r, g, b)


def find_neigh(img, x, y):
    coords = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    neigh_lst = []
    for px, py in coords:
        ignore_this = px + x < 0 or px + x > img.shape[1] - 1 or \
            py + y < 0 or py + y > img.shape[0] - 1
        if ignore_this:
            continue
        neigh_lst.append((x + px, y + py))
    return neigh_lst


def get2color(filename):
    oimg = Image.open(filename)
    gimg = np.array(oimg.convert('L'))
    img = np.array(oimg)
    zmg = np.zeros((img.shape[0] + 2, img.shape[1] + 2))
    zmg[1:-1, 1:-1] = img[:, :]
    img = zmg
    nimg = np.zeros(img.shape, dtype='uint8')
    for yndex, line in enumerate(img):
        for xndex, item in enumerate(line):
            if item == 0:
                nimg[yndex, xndex] = 1
                continue
            neigh = find_neigh(img, xndex, yndex)
            colors = np.array(list(map(lambda x: img[x[1], x[0]], neigh)))
            if 0 not in colors:
                nimg[yndex, xndex] = 1
    gimg[gimg < 127] = 0
    gimg[gimg > 127] = 1
    nimg = 1 - nimg
    gimg += nimg[1:-1, 1:-1]
    gimg[gimg > 0] = 1
    gimg = 1 - gimg
    image = Image.fromarray(gimg).convert('P')
    image.putpalette([0, 0, 0, 255, 255, 255])
    return image


def generate_picross(input_image, output_image, **kw):
    """
    extra params:
      - block_size: int, default 32
      - render_font: string, default font from resource folder
      - add_image: bool, default True
      - use_black: bool, default False
      - create_json: bool, default None
      - load_json: bool, default None
    """
    block_size = kw.get('block_size', 32)
    render_font = kw.get('render_font', 'resources/FiraMono-Regular.ttf')
    use_black = kw.get('use_black', False)
    add_image = kw.get('add_image', True)

    if kw.get('load_json'):
        with open(input_image, 'r') as f:
            data = js.load(f)

            arr = np.array(data['gamepole'], dtype='uint8')
            palette = data['palette']

            img = Image.fromarray(arr).convert('P')
            img.putpalette(palette)

            horizontal_data = data['horizontal']
            vertical_data = data['vertical']

            if len(palette) == 2 * 3:
                background_color = 'white'
            else:
                background_color = (0, 0, 0, 0)
                img.info['transparency'] = 0
    else:
        if use_black:
            # делаем из цветной картинки двухцветную
            img = get2color(input_image)
            background_color = 'white'
        else:
            # читаем картинку и преобразуем цвета в палитру
            img = Image.open(input_image).convert('P')
            background_color = (0, 0, 0, 0)

        # получаем все цвета палитры
        palette = bytearray(img.palette.palette)

        # получаем последовательности цветов на картинке
        arr = np.array(img)
        horizontal_data = get_tuples(arr, one_color=use_black)
        vertical_data = get_tuples(arr.T, one_color=use_black)

        if kw.get('create_json'):
            with open(output_image, 'w') as f:
                data = {
                    'palette': list(palette),
                    'horizontal': list(horizontal_data),
                    'vertical': list(vertical_data),
                    'gamepole': arr.tolist()
                }
                js.dump(data, f)
            return

    # находим самый длинный блок
    horizontal_blocks = 0
    for item in horizontal_data:
        horizontal_blocks = max(len(item), horizontal_blocks)
    vertical_blocks = 0
    for item in vertical_data:
        vertical_blocks = max(len(item), vertical_blocks)

    # расчитываем размер новой картинки
    nimage_width = block_size * img.size[0] + horizontal_blocks * block_size
    nimage_height = block_size * img.size[1] + vertical_blocks * block_size

    nimage = Image.new('RGBA', (nimage_width + 1, nimage_height + 1), background_color)
    draw = ImageDraw.Draw(nimage)

    # позиция картинки
    box = (horizontal_blocks * block_size, vertical_blocks * block_size, nimage_width, nimage_height)
    if add_image:
        # ресайзим старую картинку
        picture = img.resize((block_size * img.size[0], block_size * img.size[1]), Image.BILINEAR)
        # и переносим на новую
        nimage.paste(picture, box=box)
    # рисуем рамку
    draw.rectangle(box, outline='black')

    # рисуем клеточки
    for x in range(horizontal_blocks * block_size, nimage_width + 1, block_size):
        draw.line((x, 0, x, nimage_height), 'black')
    for x in range(0, horizontal_blocks * block_size, block_size):
        draw.line((x, vertical_blocks * block_size, x, nimage_height), 'black')
    for y in range(vertical_blocks * block_size, nimage_height + 1, block_size):
        draw.line((0, y, nimage_width, y), 'black')
    for y in range(0, vertical_blocks * block_size, block_size):
        draw.line((horizontal_blocks * block_size, y, nimage_width, y), 'black')

    # растановляем числовые значения для цветов
    font = ImageFont.truetype(render_font, size=block_size - 10)
    for xindex, line in enumerate(vertical_data):
        ypos = (vertical_blocks - len(line) + 0.1) * block_size
        xpos = block_size * (horizontal_blocks + 0.3 + xindex)
        for color, number in line:
            # TODO: нужен нормальный фикс
            number_str = str(number)
            xdelta = -6 if len(number_str) > 1 else 0
            draw.text((xpos + xdelta, ypos), number_str, font=font, fill=get_color(palette, color))
            ypos += block_size
    for yindex, line in enumerate(horizontal_data):
        xpos = (horizontal_blocks - len(line) + 0.3) * block_size
        ypos = block_size * (vertical_blocks + yindex + 0.1)
        for color, number in line:
            # TODO: нужен нормальный фикс
            number_str = str(number)
            xdelta = -6 if len(number_str) > 1 else 0
            draw.text((xpos + xdelta, ypos), number_str, font=font, fill=get_color(palette, color))
            xpos += block_size

    nimage.convert('P').save(output_image)


if __name__ == '__main__':
    generate_picross('resources/mario.png', 'resources/mario-picross.json', use_black=False, create_json=True)
    generate_picross('resources/mario-picross.json', 'resources/mario-picross.png', use_black=False, load_json=True)
