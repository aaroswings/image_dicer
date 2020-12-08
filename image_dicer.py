import argparse
import math
from pathlib import Path
import PIL
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

parser = argparse.ArgumentParser(description='IMAGE CHIPPING FUNCTIONS')
parser.add_argument('-i', '--input_dir', type=str, metavar='str', help='path to input files to be processed')
parser.add_argument('-o', '--output_dir', type=str, metavar='str', help='path to output directory')
parser.add_argument('--max_size', type=int, default=2048, metavar='str',
                    help='maximum size of long edge')
parser.add_argument('--max_edge_ratio', type=int, default=1.0, metavar='str', help='maximum image edge ratio')
parser.add_argument('--fileglob', nargs='+', help='File extensions of input in form *.png, *.jpg etc')

opt = parser.parse_args()
print(opt)

def resize_by_long_edge(img, max_size=2048):
    original_size = max(img.size[0], img.size[1])

    if original_size >= MAX_SIZE:
        if (img.size[0] > img.size[1]):
            resized_width = MAX_SIZE
            resized_height = int(round((MAX_SIZE/float(img.size[0]))*img.size[1])) 
        else:
            resized_height = MAX_SIZE
            resized_width = int(round((MAX_SIZE/float(img.size[1]))*img.size[0]))

        img = img.resize((resized_width, resized_height), img.ANTIALIAS)
    return img

def crop_by_ratio(img, max_aspect_ratio=1.25):
    '''
    Split the image up into multiple parts along the long edge if it exceeds a certain aspect ratio.
    '''
    long_edge = max(img.size[0], img.size[1])
    short_edge = min(img.size[0], img.size[1])

    transposed = False

    if long_edge / short_edge > max_aspect_ratio:
        '''
        Rotate all images so that the long edge is the horizontal edge before slicing, 
        then unrotate the slices individually..
        '''
        if long_edge == img.size[1]:
            img = img.transpose(method=PIL.Image.ROTATE_90)
            transposed = True

        n_crops = math.ceil(long_edge / short_edge)

        for i in range(n_crops - 1):
            box = (i * img.size[1],  0, (i+1) * img.size[1], img.size[1])
            cropped = img.crop(box)

            if transposed:
                yield cropped.transpose(method=PIL.Image.ROTATE_270)
            else:
                yield cropped

        cropped = img.crop((img.size[0] - img.size[1], 0, img.size[0], img.size[1]))

        if transposed:
            yield cropped.transpose(method=PIL.Image.ROTATE_270)
        else:
            yield cropped

def crop(img, height, width):
    for i in range(img.size[1]//height):
        for j in range(img.size[0]//width):
            box = (j*width, i*height, (j+1)*width, (i+1)*height)
            yield img.crop(box)

if opt.input_dir is not None:
    output_dir = opt.output_dir
    if output_dir is None:
        output_dir = opt.input_dir

    in_directory = Path(opt.input_dir)
    for ext in opt.fileglob:
        for filename in in_directory.glob(ext):
            img = Image.open(filename)
            for crop_i, cropped in enumerate(crop_by_ratio(img, opt.max_edge_ratio)):
                resized = resize_by_long_edge(cropped, opt.max_size)
                with open(opt.output_dir / f'{filename.name}_slice_{crop_i}.jpg', 'wb+') as f:
                    resized.save(f)

