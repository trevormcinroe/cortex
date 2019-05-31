from __future__ import absolute_import, division, print_function
import tensorflow as tf
import numpy as np
import os
import matplotlib.image as mpimg
import shutil
from random import shuffle
import time
import json


def img_cc_checker(img_folder, silent=True):
    '''A helper function to skim through a folder of images and alert the user if some images are not 3CC
    Args:
        img_folder: a full path to the folder containing the images to scan, str
        silent: make it talk, bool
    Returns:
        a list of full paths to the bad images
    '''
    assert os.path.isdir(img_folder), 'img_folder is not real, silly'

    # Init list
    bad_imgs = []

    # Image full paths
    img_full_paths = [os.path.join(img_folder, x)
                      for x in [x for x in os.listdir(img_folder)]]

    # Looping through images. Raising hand if the image does not have a CC attribute (could be greyscale, etc)
    for img in img_full_paths:
        try:
            mpimg.imread(img).shape[2]
        except:
            bad_imgs.append(img)
            if silent == False:
                print('We found one, boss...')

    return bad_imgs

def file_rename(top_dir, data_dir, train_pct, silent=True):
    '''A helper function that renames files in the format classname_number
    Args:
        top_dir: path to the folder that contains the folders of the classes that contain the image data
        data_path: path to the ultimate folder that will contain our renamed data
        train_pct: the percentage of the data to use as the training set
        silent: a switch to control the output of information
    Returns:
        a class_names_to_ids dict, {class_num, 'class_str'}
    '''
    # Creating global references
    isdir = os.path.isdir
    pathjoin = os.path.join
    listdir = os.listdir
    rename = os.rename
    rmdir = os.rmdir
    # Creating the data folder if it does not already exist
    if not isdir(data_dir):
        os.mkdir(data_dir)

    # This is to report on how long it took this action to complete
    start = time.time()

    # == Getting the full paths to each of our image classes ==#
    # A list for the class names
    class_names = listdir(top_dir)

    # Creating a dict to return of this list
    class_names_to_ids = dict(zip(class_names, range(len(class_names))))

    # Full paths to the folders
    class_path = [pathjoin(top_dir, folder) for folder in class_names]

    # Looping through each class_path
    for i in range(len(class_path)):

        # Getting a list of the files in each class_path
        ll = [pathjoin(class_path[i], file) for file in listdir(class_path[i])]

        # Looping through filenames and renaming them to the data_dir
        for z in range(len(ll)):
            rename(src=ll[z],
                   dst=pathjoin(data_dir,
                                class_names[i] + '__' + str(z) + '.jpg'))

    # Deleting images that are not 3cc before we create the train/test folders
    bad_imgs = img_cc_checker(img_folder=data_dir)
    for img in bad_imgs:
        os.remove(img)

    # Geting a list of the file names in data to be shuffled
    data_files = [x for x in listdir(data_dir)]
    shuffle(data_files)
    data_files_train = data_files[:int(np.round(len(data_files) * train_pct))]
    data_files_test = [x for x in data_files if x not in data_files_train]

    # Now creating a new folder for train. Need to do this after so there
    # Are no conflicts with moving folders into each other
    if not isdir(pathjoin(data_dir, 'train')):
        os.mkdir(pathjoin(data_dir, 'train'))
    if not isdir(pathjoin(data_dir, 'test')):
        os.mkdir(pathjoin(data_dir, 'test'))



    # Now moving files into the train/test folders
    for train_file in data_files_train:
        rename(src=pathjoin(data_dir, train_file),
               dst=pathjoin(data_dir, 'train', train_file))

    for test_file in data_files_test:
        rename(src=pathjoin(data_dir, test_file),
               dst=pathjoin(data_dir, 'test', test_file))

    # Deleting the old shell folders
    for folder in listdir(top_dir):
        rmdir(pathjoin(top_dir, folder))

    # Writing the labels dictionary to a .txt file
    with open(pathjoin(data_dir, 'labels.txt'), 'w') as f:
        f.write(json.dumps(class_names_to_ids))

    if silent == False:
        # Message of doneness
        img_len = len(data_files)
        train_len = len(listdir(pathjoin(data_dir, 'train')))
        test_len = len(listdir(pathjoin(data_dir, 'test')))
        full_time = time.time() - start
        print(f'Rename complete. You renamed {img_len} images. This action took {full_time} seconds.')
        print(f'\n Your training folder contains {train_len} images. \n Your testing folder contains {test_len} images.')
        return class_names_to_ids
    else:
        return class_names_to_ids

class tfrecord_generator():
    def __init__(self, labels):
        self.labels = labels

    def convert_image_folder(self, img_folder, tfrecord_file_name):
        # Get all file names of images present in folder
        img_paths = os.listdir(img_folder)
        img_paths = [os.path.abspath(os.path.join(img_folder, i)) for i in img_paths]

        with tf.python_io.TFRecordWriter(tfrecord_file_name) as writer:
            for img_path in img_paths:
                example = self._convert_image(img_path)
                writer.write(example.SerializeToString())

    def _convert_image(self, img_path):
        label = self._get_label_with_filename(img_path)
        img_shape = mpimg.imread(img_path).shape
        filename = os.path.basename(img_path)

        # Read image data in terms of bytes
        with tf.gfile.FastGFile(img_path, 'rb') as fid:
            image_data = fid.read()

        example = tf.train.Example(features=tf.train.Features(feature={
            'filename': tf.train.Feature(bytes_list=tf.train.BytesList(value=[filename.encode('utf-8')])),
            'rows': tf.train.Feature(int64_list=tf.train.Int64List(value=[img_shape[0]])),
            'cols': tf.train.Feature(int64_list=tf.train.Int64List(value=[img_shape[1]])),
            'channels': tf.train.Feature(int64_list=tf.train.Int64List(value=[img_shape[2]])),
            'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_data])),
            'label': tf.train.Feature(int64_list=tf.train.Int64List(value=[label])),
        }))
        return example

    def _get_label_with_filename(self, filename):
        basename = os.path.basename(filename).split('.')[0]
        basename = basename.split('__')[0]
        return self.labels[basename]


class tfrecord_extractor():
    def __init__(self, tfrecord_file):
        self.tfrecord_file = os.path.abspath(tfrecord_file)

    def _extract_fn(self, tfrecord):
        # Extract features using the keys set during creation
        features = {
            'filename': tf.FixedLenFeature([], tf.string),
            'rows': tf.FixedLenFeature([], tf.int64),
            'cols': tf.FixedLenFeature([], tf.int64),
            'channels': tf.FixedLenFeature([], tf.int64),
            'image': tf.FixedLenFeature([], tf.string),
            'label': tf.FixedLenFeature([], tf.int64)
        }

        # Extract the data record
        sample = tf.parse_single_example(tfrecord, features)

        image = tf.image.decode_image(sample['image'])
        img_shape = tf.stack([sample['rows'], sample['cols'], sample['channels']])
        label = sample['label']
        filename = sample['filename']
        return [image, label, filename, img_shape]

    def extract_image(self):
        # Create folder to store extracted images
        folder_path = './ExtractedImages'
        shutil.rmtree(folder_path, ignore_errors=True)
        os.mkdir(folder_path)

        # Pipeline of dataset and iterator
        dataset = tf.data.TFRecordDataset([self.tfrecord_file])
        dataset = dataset.map(self._extract_fn)
        iterator = dataset.make_one_shot_iterator()
        next_image_data = iterator.get_next()

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            image_data = sess.run(next_image_data)
            return image_data


top_dir = '//10.176.176.135/qdr_synapse/data/food-101/images'
data_dir = '//10.176.176.135/qdr_synapse/data/food-101/data'

class_dict = file_rename(top_dir=top_dir, data_dir=data_dir, train_pct=.8, silent=False)

t = tfrecord_generator(labels=class_dict)
t.convert_image_folder(img_folder='//10.176.176.135/qdr_synapse/data/food-101/data/train',
                       tfrecord_file_name='//10.176.176.135/qdr_synapse/data/food-101/data/train.tfrecord')
t.convert_image_folder(img_folder='//10.176.176.135/qdr_synapse/data/food-101/data/test',
                       tfrecord_file_name='//10.176.176.135/qdr_synapse/data/food-101/data/test.tfrecord')

