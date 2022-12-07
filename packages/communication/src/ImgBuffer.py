from typing import Set
import numpy as np
from img_analysis import get_maxes, Point


class ImgBuffer:
    """
    This class encapsulate all the image stream processing
    """
    def __init__(self, buffer_size: int, forget_time: int):
        # the amount of frames to be stored. It should be around twice the lowest frequency and half the framerate
        self.buffer_size = buffer_size
        # the amount of frames where no change of intensity is detected before a point is removed
        self.forget_time = forget_time

        # the last raw image
        self.prev_raw_img: np.ndarray = None
        # set of active points
        self.points: Set[Point] = set()

    def push(self, new_img: np.ndarray):
        """
        This function creates new points using the difference between it and the previous image. It then gives the
        inputted image to all known points so that they can update their internal buffers

        :param new_img: an image in the form of a ndarray
        """
        # if a previous frame exists, calculate the diff between the previous and current image
        diff_img = None
        if self.prev_raw_img is not None:
            diff = np.abs(new_img.astype(int) - self.prev_raw_img)
            diff[diff < 50] = 0
            diff_img = diff

        # if a diff exists, calculate points using the local maximums of the diff and merge them to older points
        if diff_img is not None:
            max_points = get_maxes(diff_img)
            self.points = set(Point.group_point([*max_points, *self.points], 6))

        # update all points by giving them the frame and updating the last_seen value
        for point in self.points:
            point.add_frame(new_img)
            point.last_seen += 1

        self.prev_raw_img = new_img
        
        self._trim_size()

    def _trim_size(self):
        """this method makes sure existing points' buffers are of the right size and are not too old"""
        for point in self.points.copy():
            # if a point has not been detected for forget_time frames, the point is removed
            if point.last_seen > self.forget_time:
                self.points.remove(point)
            else:
                # if a point has not been removed, crop it's buffer to be of the right size
                point.histogram = point.histogram[-self.buffer_size:]