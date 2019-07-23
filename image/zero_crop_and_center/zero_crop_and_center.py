# Script that reads in PNG gray-scale images in one directory and
# (1) crops the images by removing all 0 rows and columns from
#     top and bottom;
# (2) calculates the center of mass and centers the cropped images
#     from (1) withing a bigger image
#
# Sebastian Raschka
# Last updated: 07/23/2018

import os
import argparse
import numpy as np
import imageio
from scipy.ndimage.measurements import center_of_mass
import math


def find_zero_bounding_box(image_array):

    if len(image_array.shape) != 2:
        raise ValueError(f'Only 2D arrays are supported.\n'
                         f'Got {len(image_array.shape)} array.')

    # crop top
    start_row = 0
    for row in image_array:
        is_zero = not sum([col for col in row])
        if is_zero:
            start_row += 1
        else:
            break

    # crop bottom
    end_row = image_array.shape[0]-1
    for row in np.flip(image_array, axis=0):
        is_zero = not sum([col for col in row])
        if is_zero:
            end_row -= 1
        else:
            break

    # crop left
    start_col = 0
    for row in image_array.T:
        is_zero = not sum([col for col in row])
        if is_zero:
            start_col += 1
        else:
            break

    # crop right
    end_col = image_array.shape[0]-1
    for row in np.flip(image_array.T, axis=0):
        is_zero = not sum([col for col in row])
        if is_zero:
            end_col -= 1
        else:
            break

    return start_row, end_row+1, start_col, end_col+1


def center_in_image(image_array, output_size):

    output_array = np.zeros(output_size, dtype=np.uint8)

    if len(image_array.shape) != 2:
        raise ValueError(f'Only 2D image arrays are supported.\n'
                         f'Got {len(image_array.shape)} array.')

    if len(image_array.shape) != 2:
        raise ValueError(f'Only 2D output image arrays are supported.\n'
                         f'Got {len(output_array.shape)} array.')

    if output_array.shape[0] <= image_array.shape[0]:
        raise ValueError(f'Input array must not be taller than input array.\n'
                         f'Got {image_array.shape[0]} and {output_array.shape[0]}.')

    if output_array.shape[1] <= image_array.shape[1]:
        raise ValueError(f'Input array must not be wider than input array.\n'
                          'Got {image_array.shape[1]} and {output_array.shape[1]}.')

    y_center, x_center = center_of_mass(image_array)
    y_center, x_center = math.floor(y_center), math.floor(x_center)

    y_center_out = output_array.shape[0] // 2
    x_center_out = output_array.shape[1] // 2

    x_diff = x_center_out - x_center
    y_diff = y_center_out - y_center

    output_array[y_diff:image_array.shape[0]+y_diff, 
                 x_diff:image_array.shape[1]+x_diff] = image_array

    return output_array


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description='',
            epilog=""":
python zero_crop_and_center --in_dir './some_pngs'/\\
   --out_dir './centered_pngs' --out_height 28 --out_width 28""",
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--in_dir',
                        required=True,
                        type=str,
                        help='Directory with input images')
    parser.add_argument('-o', '--out_dir',
                        type=str,
                        required=True,
                        help='Directory with output images')

    parser.add_argument('--out_height',
                        type=int,
                        required=True,
                        help='Height of the output images')

    parser.add_argument('--out_width',
                        type=int,
                        required=True,
                        help='Width of the output images')

    parser.add_argument('--version', action='version', version='v. 1.0')

    args = parser.parse_args()

    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)

    png_names = [i for i in os.listdir(args.in_dir) if i.endswith('.png')]
    if not len(png_names):
        raise ValueError(f'No .png files found in {args.in_dir}')

    in_paths = [os.path.join(args.in_dir, i) for i in png_names]
    out_paths = [os.path.join(args.out_dir, i) for i in png_names]

    for in_img, out_img in zip(in_paths, out_paths):
        img = imageio.imread(in_img)
        top, bottom, left, right = find_zero_bounding_box(img)
        cropped_img = img[top:bottom, left:right]

        centered_img = center_in_image(image_array=img[top:bottom, left:right],
                                       output_size=(args.out_height,
                                                    args.out_width))

        imageio.imsave(out_img, centered_img)