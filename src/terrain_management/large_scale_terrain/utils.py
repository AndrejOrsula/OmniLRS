__author__ = "Antoine Richard"
__copyright__ = (
    "Copyright 2024, Space Robotics Lab, SnT, University of Luxembourg, SpaceR"
)
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Antoine Richard"
__email__ = "antoine.richard@uni.lu"
__status__ = "development"

from scipy.interpolate import CubicSpline
from typing import Tuple
import dataclasses
import numpy as np
import threading
import time


@dataclasses.dataclass
class BoundingBox:
    x_min: float = 0
    x_max: float = 0
    y_min: float = 0
    y_max: float = 0

@dataclasses.dataclass
class RockBlockData:
    coordinates: np.ndarray = dataclasses.field(default_factory=np.ndarray)
    quaternion: np.ndarray = dataclasses.field(default_factory=np.ndarray)
    scale: np.ndarray = dataclasses.field(default_factory=np.ndarray)
    ids: np.ndarray = dataclasses.field(default_factory=np.ndarray)

@dataclasses.dataclass
class CraterMetadata:
    radius: float = 0.0
    coordinates: Tuple[int, int] = (0, 0)
    deformation_spline_id: CubicSpline = None
    marks_spline_id: CubicSpline = None
    marks_intensity: float = 0
    crater_profile_id: int = 0
    xy_deformation_factor: Tuple[float, float] = (0, 0)
    rotation: float = 0

    def get_memory_footprint(self) -> int:
        return self.size


class ScopedTimer:
    _thread_local_data = threading.local()

    def __init__(self, name, active=True, argb_color=None):
        self.name = name
        self.active = active
        self.argb_color = argb_color
        if argb_color:
            self.rgb_color = self.argb_to_rgb(argb_color)
            self.ansi_color = self.rgb_to_ansi(self.rgb_color)
        else:
            self.ansi_color = ""
        self.indent = 2  # Number of spaces to indent per nesting level

    def argb_to_rgb(self, argb):
        rgb = (argb >> 16) & 0xFFFFFF
        return (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF

    def rgb_to_ansi(self, rgb):
        return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"

    def __enter__(self):
        if self.active:
            if not hasattr(self._thread_local_data, 'nesting_level'):
                self._thread_local_data.nesting_level = 0
            if not hasattr(self._thread_local_data, 'messages'):
                self._thread_local_data.messages = []

            self._thread_local_data.nesting_level += 1
            self.start_time = time.time()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.active:
            self.end_time = time.time()
            elapsed_time = self.end_time - self.start_time
            reset_color = "\033[0m"
            indentation = ' ' * (self._thread_local_data.nesting_level - 1) * self.indent
            message = f"{self.ansi_color}{indentation}{self.name} took: {elapsed_time:.4f} seconds{reset_color}"
            
            # Insert the message at the beginning of the list to ensure the outermost message is printed first
            self._thread_local_data.messages.insert(0, message)

            self._thread_local_data.nesting_level -= 1

            # If we are back to the outermost level, print all accumulated messages
            if self._thread_local_data.nesting_level == 0:
                for msg in self._thread_local_data.messages:
                    print(msg)
                # Clear the message stack
                self._thread_local_data.messages.clear()