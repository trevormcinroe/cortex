import numpy as np
from math import sqrt
import random
import scipy.ndimage
gf = scipy.ndimage.filters.gaussian_filter
unif = np.random.uniform

# TODO: add ability to do differently shaped occlusions


def random_erasing(image):
    '''A helper function that randomly erases positions of the image akin to: https://arxiv.org/pdf/1708.04896.pdf
    Args:
        image: an image, np.array
    Returns
        a modified image, np.array
    '''

    # Get area of image
    area = image.shape[0] * image.shape[1]

    # Aspect ratio
    aspect_ratio = unif(.3, 1 / .3)

    # Area of erase
    target_area = unif(0.02, 0.2) * area

    # Height and width of the square
    h = int(round(sqrt(target_area * aspect_ratio)))
    w = int(round(sqrt(target_area / aspect_ratio)))

    # Picking the starting pixel
    x1 = random.randint(0, image.shape[0] - h)
    y1 = random.randint(0, image.shape[1] - w)

    image[x1:x1 + h, y1:y1 + w, 0] = np.mean(image[:, :, 0])
    image[x1:x1 + h, y1:y1 + w, 1] = np.mean(image[:, :, 1])
    image[x1:x1 + h, y1:y1 + w, 2] = np.mean(image[:, :, 2])

    return image


def random_crop(image, w, h):
    '''A helper function to take random (w x h) crops of an image
    Args:
        image: an image, np.array
        w: desired width of the image, int
        h: desired height of the image, int
    Returns:
        a random crop of an image, np.array
    '''
    # Asserts
    assert w <= image.shape[0], 'w is larger than image dimensions'
    assert h <= image.shape[1], 'h is larger than image dimensions'

    # The max value for starting pixel (x, y) is (array_rows - h, array_cols - w)
    starting_x = random.randint(0, image.shape[0] - h - 1)
    starting_y = random.randint(0, image.shape[1] - w - 1)

    return image[starting_x:starting_x + h, starting_y:starting_y + w, :]


def rotation(image, level):
    '''A helper function to rotate images CCW
    Args:
        image: an image, np.array
        level: how many times to rotate: [1, 2, 3] == [90, 180, 270]
    Returns:
        a rotated image, np.array
    '''
    if level == 1:
        image[:, :, 0] = image[:, :, 0].T
        image[:, :, 1] = image[:, :, 1].T
        image[:, :, 2] = image[:, :, 2].T
        return image

    if level == 2:
        image[:, :, 0] = np.rot90(image[:, :, 0].T)
        image[:, :, 1] = np.rot90(image[:, :, 1].T)
        image[:, :, 2] = np.rot90(image[:, :, 2].T)
        return image

    if level == 3:
        image[:, :, 0] = image[::-1, :, 0].swapaxes(-2, -1)
        image[:, :, 1] = image[::-1, :, 1].swapaxes(-2, -1)
        image[:, :, 2] = image[::-1, :, 2].swapaxes(-2, -1)
        return image


def gaussian_blue(image, sigma):
    '''A helper function to apply a gaussian blur to an image
    Args:
        image: an image, np.array
        sigma: standard deviation of the Gaussian kernel, numeric (lower sigma == faster)
    Returns:
        a blurred image, np.array
    '''

    return np.dstack((gf(image[:, :, 0], sigma),
                      gf(image[:, :, 1], sigma),
                      gf(image[:, :, 2], sigma)))
