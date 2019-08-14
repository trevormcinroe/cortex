"""
This module contains functions and processes for efficiently splitting video data into frames.

author: Trevor McInroe
date last updated: 8.13.2019
v: 1.0
"""

import numpy as np
import time
import cv2
import os
import multiprocessing
import random
### === TESTING OUT CV2 === ###

# Length = 00:12:50
# 1920x1048
# Bitrate = 3,136 kbps
# Frames: 60/second

file = r'\\10.176.176.135\Quadratic\Decision Sciences\MLB\vidz\london_game\2019-08-12 16-01-28.mp4'


def vid_to_img(video, folder_name):
    """"""

    assert os.path.isfile(video), 'given video cannot be found'

    # Creating a nested folder to place the images into
    if not os.path.isdir(folder_name):

        os.mkdir(folder_name)

    # Does not read it into memory, thank goodness...
    # What does this actually do?
    vid = cv2.VideoCapture(video)

    frame_cnt = 0
    # break_condition = True
    while frame_cnt < 100:

        inner_count = 0

        while inner_count <= 80:
            # Reading a single frame
            ret, frame = vid.read()

            if ret:

                inner_count += 1

            else:

                break

        cv2.imwrite(os.path.join(folder_name, str(frame_cnt) + 'london.png'),
                    frame)

        frame_cnt += 1


# Testing out a different implementation
def vid_to_img2(video, folder_name, est_vid_len, n, game):
    """"""

    assert os.path.isfile(video), 'given video cannot be found'

    # Creating a nested folder to place the images into
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    # Does not read it into memory, thank goodness...
    # What does this actually do?
    vid = cv2.VideoCapture(video)

    fps = vid.get(cv2.CAP_PROP_FPS)

    # est_vid_length is in minutes
    est_tot_frames = fps * est_vid_len * 60

    desired_frames = n * np.arange(est_tot_frames)


    for i in desired_frames:

        vid.set(1, i - 1)

        success, img = vid.read(1)

        cv2.imwrite(os.path.join(folder_name, str(i) + game + '.png'), img)

    vid.release()


def vid_to_img3(video, folder_name, n, game):
    """"""

    assert os.path.isfile(video), 'given video cannot be found'

    # Creating a nested folder to place the images into
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    # Does not read it into memory, thank goodness...
    # What does this actually do?
    vid = cv2.VideoCapture(video)

    count = 0

    while vid.isOpened():

        success, img = vid.read()

        if success:

            cv2.imwrite(os.path.join(folder_name, str(count) + game + '.png'), img)

            count += n

            vid.set(1, count)

        else:

            vid.release()

            break

class Vid_To_Img:
    """This class is meant to handle the parallelization of video-to-image parsing
    Due to the nature of the size of video data (read: B I G), running parallel processes is a
    necessary evil.

    This process works by observing the length of the video, in frames, and then splitting that
    length up into n_parallel segments. This is accomplished with the .initalize() method.

    Once the class has been initalized for a given video, the .parallel_parse() method can be called.
    This method spawns a parallel process of the .single_parse() method

    """

    def __init__(self,
                 video_file,
                 n_parallel,
                 nth_frame,
                 save_folder):

        self.video_file = video_file
        self.video = None
        self.video_len = None
        self.n_parallel = n_parallel
        self.nth_frame = nth_frame
        self.save_folder = save_folder
        self.job_dict  = {}


    def initalize(self):
        """"""

        # assert os.path.isfile(self.video), 'given video cannot be found'

        # Creating the
        if os.path.isdir(self.save_folder):

            answer = input(f'Given save_folder exists. Are you sure you want to write images here? (y/n)')

            if answer == 'n':

                print('Please re-assign the self.save_folder attribute and try again.')

                return ' '

            if answer == 'y':

                print('creating given save folder...')

        # If the save_folder does not exist, create it
        else:

            print('given save_folder does not exist, creating...')
            os.mkdir(self.save_folder)

        # Pulling the reference to the video into memory
        video = cv2.VideoCapture(self.video_file)

        # Now init the job_dict, whose purpose is to take the video and parse it out into timestamps
        # that each single_proc is responsible for
        # This is *extremely* important in terms of parallelizing the work

        # First, we grab the length of the video...
        video.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        self.video_len = video.get(cv2.CAP_PROP_POS_MSEC) / 1000 # THIS IS THE LEN IN SECONDS

        beginning = 0
        for i in range(self.n_parallel):

            # self.job_dict[str(i)] = (beginning, round(beginning + self.video_len / self.n_parallel))


            self.job_dict[str(i)] = {}
            self.job_dict[str(i)]['start'] = beginning
            self.job_dict[str(i)]['end'] = round(beginning + self.video_len / self.n_parallel)
            self.job_dict[str(i)]['name'] = str(random.getrandbits(16))

            beginning += round(self.video_len / self.n_parallel)

    def single_parse(self, start, end, name):
        """

        Args:
            start: the frame in the video where the parsing should start, float
            end: the frame in the video where the parsing should end, float
            name: the name of the process, used to keep all parallel processes from overwriting eachother

        Returns:

        """

        assert len(self.job_dict) == self.n_parallel, 'please check your .initalization()'
        #

        # Re-initing the video locally
        local_vid = cv2.VideoCapture(self.video_file)

        # Init a frame counter. This will allow us to keep track of where in the video this
        # single process should be
        frame_counter = start

        # As our frame_counter increases, we will know when to stop parsing the video for the given
        # section by comparing it to the end of the section
        while frame_counter < end:

            # Setting the current frame in the video
            local_vid.set(1, frame_counter)

            # Extracting the video
            # We use the randomly generated name of the process to stop files from being overwritten
            success, img = local_vid.read()

            cv2.imwrite(os.path.join(self.save_folder, str(frame_counter) + '_' + name + '.png'),
                        img)

            # Incrementing the counter
            frame_counter += self.nth_frame

        # Once outside of the loop we can release the video
        # This frees up a pointer, deallocates memory, and closes the IO stream to the file
        local_vid.release()

    def parallel_parse(self):
        """"""

        assert len(self.job_dict) == self.n_parallel, 'please check your .initalization()'

        for i in range(self.n_parallel):

            p = multiprocessing.Process(target=self.single_parse,
                                        args=(self.job_dict[str(i)]['start'],
                                              self.job_dict[str(i)]['end'],
                                              self.job_dict[str(i)]['name'], ))


            p.start()
            print(f'Started job {str(i)}...')



# start = time.time()
# vid_to_img3(video=file,
#            folder_name=r'\\10.176.176.135\Quadratic\Decision Sciences\MLB\vidz\london_game\imgs',
#             n=10,
#             game='london')
#
# print(f'This operation took {time.time() - start} seconds to parse {len(os.listdir("//10.176.176.135/Quadratic/Decision Sciences/MLB/vidz/london_game/imgs"))} images')


if __name__ == '__main__':
    start = time.time()
    a = Vid_To_Img(video_file=file,
                   n_parallel=12,
                   nth_frame=10,
                   save_folder=r'\\10.176.176.135\Quadratic\Decision Sciences\MLB\vidz\london_game\imgs')

    a.initalize()

    a.parallel_parse()


    # print(f'This action took {time.time() - start} seconds!')