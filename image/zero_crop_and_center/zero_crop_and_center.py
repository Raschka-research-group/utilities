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


def find_zero_bounding_box(image_array, background_threshold=0):

    if len(image_array.shape) != 2:
        raise ValueError(f'Only 2D arrays are supported.\n'
                         f'Got {len(image_array.shape)} array.')

    # crop top
    start_row = 0
    keep_row = False
    for row in image_array:
        if keep_row:
            break

        for ele in row:
            if ele > background_threshold:
                keep_row = True
                break
        if not keep_row:
            start_row += 1

    # crop bottom
    end_row = image_array.shape[0]-1
    keep_row = False
    for row in np.flip(image_array, axis=0):
        if keep_row:
            break
        for ele in row:
            if ele > background_threshold:
                keep_row = True
                break
        if not keep_row:
            end_row -= 1

    # crop left
    start_col = 0
    keep_row = False
    for row in image_array.T:
        if keep_row:
            break
        for ele in row:
            if ele > background_threshold:
                keep_row = True
                break
        if not keep_row:
            start_col += 1

    # crop right
    end_col = image_array.shape[0]-1
    keep_row = False
    for row in np.flip(image_array.T, axis=0):
        if keep_row:
            break
        for ele in row:
            if ele > background_threshold:
                keep_row = True
                break
        if not keep_row:
            end_col -= 1

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
        raise ValueError(f'Output array must not be taller than input array.\n'
                         f'Got {image_array.shape[0]} '
                         f'and {output_array.shape[0]}.')

    if output_array.shape[1] <= image_array.shape[1]:
        raise ValueError(f'Output array must not be wider than input array.\n'
                         f'Got {image_array.shape[1]} '
                         f'and {output_array.shape[1]}.')

    y_center, x_center = center_of_mass(image_array)
    y_center, x_center = math.floor(y_center), math.floor(x_center)

    y_center_out = output_array.shape[0] // 2
    x_center_out = output_array.shape[1] // 2

    x_diff = max(0, x_center_out - x_center)
    y_diff = max(0, y_center_out - y_center)

    y_buff = 0
    x_buff = 0

    out_shape = output_array[y_diff:image_array.shape[0]+y_diff,
                             x_diff:image_array.shape[1]+x_diff]

    if out_shape.shape[0] < image_array.shape[0]:
        y_buff = image_array.shape[0] - out_shape.shape[0]

    if out_shape.shape[1] < image_array.shape[1]:
        x_buff = image_array.shape[1] - out_shape.shape[1]

    output_array[y_diff-y_buff:image_array.shape[0]+y_diff,
                 x_diff-x_buff:image_array.shape[1]+x_diff] = image_array

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

    parser.add_argument('--background_threshold',
                        type=int,
                        default=0,
                        help='Threshold for cropping a pixel. '
                             'By default, all pixels'
                             '">0" will be regared as '
                             'non-background when cropping.')

    parser.add_argument('--invert_image',
                        type=bool,
                        default=False,
                        help='Inverts the image colors if `True`.')

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

        try:
            img = imageio.imread(in_img)
            if args.invert_image:
                img = np.invert(img)
            top, bottom, left, right = find_zero_bounding_box(
                img, args.background_threshold)
            cropped_img = img[top:bottom, left:right]

            centered_img = center_in_image(image_array=img[top:bottom, left:right],
                                           output_size=(args.out_height,
                                                        args.out_width))

            imageio.imsave(out_img, centered_img)
        except Exception as e:

            print(f'Error handling file{in_img}')
            print(e)

