import argparse
import math
from pathlib import Path
import PIL
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

parser = argparse.ArgumentParser(description='IMAGE CHIPPING FUNCTIONS')
parser.add_argument('-i', '--source_dir', type=str, metavar='str', help='path to input files to be processed')
parser.add_argument('-o', '--dest_dir', type=str, metavar='str', help='path to output directory')
parser.add_argument('--max_size', type=int, default=2048, metavar='str',
                    help='maximum size of long edge')
parser.add_argument('--max_edge_ratio', type=int, default=1.0, metavar='str', help='maximum image edge ratio')
parser.add_argument('--fileglob', nargs='+', help='File extensions of input in form *.png, *.jpg etc')

opt = parser.parse_args()

def resize_by_long_edge(img, max_size=2048):
    original_size = max(img.size[0], img.size[1])

    if original_size >= max_size:
        if (img.size[0] > img.size[1]):
            resized_width = max_size
            resized_height = int(round((max_size/float(img.size[0]))*img.size[1])) 
        else:
            resized_height = max_size
            resized_width = int(round((max_size/float(img.size[1]))*img.size[0]))

        img = img.resize((resized_width, resized_height), Image.ANTIALIAS)
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

if opt.source_dir is not None:
    dest_dir = opt.dest_dir
    if dest_dir is None:
        dest_dir = opt.source_dir

    in_directory = Path(opt.source_dir)
    for ext in opt.fileglob:
        for filename in in_directory.glob(ext):
            img = Image.open(filename)
            for crop_i, cropped in enumerate(crop_by_ratio(img, opt.max_edge_ratio)):
                resized = resize_by_long_edge(cropped, opt.max_size)
                with open(f'{opt.dest_dir}/{filename.name}_slice_{crop_i}.jpg', 'wb+') as f:
                    resized.save(f)


