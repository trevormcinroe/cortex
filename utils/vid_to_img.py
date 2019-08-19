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
import argparse
### === TESTING OUT CV2 === ###

# Length = 00:12:50
# 1920x1048
# Bitrate = 3,136 kbps
# Frames: 60/second

file = r'\\10.176.176.135\Quadratic\Decision Sciences\MLB\vidz\london_game\2019-08-12 16-01-28.mp4'


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

            answer = input('Given save_folder exists. Are you sure you want to write images here? (y/n)')

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

        # Multiplying the number of seconds by the Frames Per Second of the video
        self.video_len = self.video_len * video.get(cv2.CAP_PROP_FPS)

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



if __name__ == '__main__':

    # CLI Utils
    parser = argparse.ArgumentParser()

    parser.add_argument('-file', help='the video file to be parsed into frames')
    parser.add_argument('-n', help='the number of parallel processes to spawn',  type=int)
    parser.add_argument('-nth', help='when skipping frames, take the nth frame', type=int)
    parser.add_argument('-save', help='the folder in which to save the parsed frames')

    args = parser.parse_args()

    # After parsing out the args, we can init the class...
    a = Vid_To_Img(video_file=args.file,
                   n_parallel=args.n,
                   nth_frame=args.nth,
                   save_folder=args.save)

    # Running the initalization of the class
    a.initalize()

    # gogogo
    a.parallel_parse()
