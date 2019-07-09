import os
import random
from shutil import copy2


def image_grab(raw_folder):
    """

    Args:
        raw_folder:

    Returns:

    """

    # Assert that there are images in raw folder and that the sorted folders exist
    assert os.path.isdir(raw_folder), 'raw_folder does not exist'

    # If the raw_folder that we point at contains non-images, we need to filter those out
    # As far as I have tested, the fastest way to do this is with a WHILE block
    # that uses the file extension as the break condition
    break_condition = ' '

    while break_condition not in ['jpg', 'jpeg', 'png']:

        # Pulling out a random image from a folder
        rand_image = os.listdir(raw_folder)[random.randint(0, len(os.listdir(raw_folder))-1)]

        # Splitting the name of the file on the '.', reversing the list, and taking the 0th element
        # This approach is agnostic to the number of '.' in a filename
        break_condition = rand_image.split('.')[::-1][0].lower()


    # Returning the full path of the image
    # This full path will be used such that the frontend can display the image
    # return os.path.join(raw_folder, rand_image)
    # print(rand_image)
    return os.path.join(rand_image)


def image_sort(raw_folder, image, sorted_folder, selection):
    """

    Args:
        image: the filepath to the image being sorted,  str
        sorted_folder:
        selection: the user's selection for the class, str

    Returns:

    """
    assert os.path.isdir(raw_folder), 'raw_folder does not exist'
    assert os.path.isdir(os.path.join(sorted_folder, 'logo')), 'logo folder does not exist'
    assert os.path.isdir(os.path.join(sorted_folder, 'no_logo')), 'no_logo folder does not exist'

    # The filepath of the image needs to be resorted here as it comes in the form: ../static/images/file.png
    image = image.replace('\\', '//').split('//')[len(image.replace('\\', '//').split('//'))-1]

    # Making a copy of the image within the sorted folder
    # That's right... a COPY. We need to retain the raw data
    copy2(src=os.path.join(raw_folder, image), dst=os.path.join(sorted_folder, selection))
