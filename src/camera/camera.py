from datetime import datetime
from typing import AnyStr, NoReturn, Any
from subprocess import call as subproc_call, check_output, SubprocessError
from logging import (
    basicConfig,
    getLogger,
    StreamHandler,
    Formatter,
    Logger,
    INFO
)

import cv2

from project import LOG_FILE_PATH, LOGGING_FORMAT


class Camera(object):
    """
    Class for reading frames from or getting/setting control values for a camera.
    """

    basicConfig(
        level=INFO,
        filename=LOG_FILE_PATH,
        format=LOGGING_FORMAT,
        datefmt='%H:%M:%S',
        filemode='w+'
    )

    stream_handler = StreamHandler()
    stream_handler.formatter = Formatter(LOGGING_FORMAT)

    logger: Logger = getLogger(__name__)
    logger.addHandler(stream_handler)

    def __init__(self, src=0, device_name="video0", control_names=None):
        """
        :param src: VideoCapture source device id or filename.
        :type src: int | str
        :param device_name: Camera device name (use `uvcdynctrl --list`).
        :type device_name: str
        :param control_names: Dictionary mapping control names used by the
            Flask application/web interface to the control names used by
            the device (use `uvcdynctrl --list` to obtain a list).
        :type control_names: dict
        """

        self.camera_fps = 24
        self.screen_width = 640
        self.screen_height = 480

        self.device_name = device_name

        self.video_capture = cv2.VideoCapture(src)

        if control_names is None:
            control_names = dict()

        autoexposure = control_names.get("autoexposure",  "Exposure, Auto")
        autofocus = control_names.get("autofocus", "Focus, Auto")
        brightness = control_names.get("brightness", "Brightness")
        contrast = control_names.get("contrast", "Contrast")
        exposure = control_names.get("exposure", "Exposure (Absolute)")
        focus = control_names.get("focus", "Focus (absolute)")
        saturation = control_names.get("saturation", "Saturation")
        zoom = control_names.get("zoom", "Zoom, Absolute")

        self.control_names = {
            "autoexposure": autoexposure,
            "autofocus": autofocus,
            "brightness": brightness,
            "contrast": contrast,
            "exposure": exposure,
            "focus": focus,
            "saturation": saturation,
            "zoom": zoom
        }

    def __del__(self):
        self.video_capture.release()

    def get_frame(self):
        """
        Read a frame from the VideoCapture object stream, superimpose a
        timestamp on the frame, and return it encoded as a JPG.
        """

        grabbed, frame = self.video_capture.read()

        if not grabbed:
            self.video_capture.release()

        frame = cv2.resize(frame, (self.screen_width, self.screen_height))
        height, width = frame.shape[:2]
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        cv2.putText(
            frame, timestamp, (int(0.02 * width), int(0.98 * height)),
            cv2.FONT_HERSHEY_COMPLEX_SMALL, .7, (250, 250, 250), 1, 20, False
        )
        frame_jpg = cv2.imencode(".jpg", frame)[1]
        return frame_jpg

    def set_fps(self, fps: int = 24) -> NoReturn:
        self.video_capture.set(cv2.CAP_PROP_FPS, fps)

    def set_control_value(self, control: AnyStr, value: Any) -> NoReturn:
        """
        Call uvcdynctrl in a subprocess to set a control value.

        :param control: Control name/type (e.g., "zoom").
        :type control: str
        :param value: New value to set.
        :type value: int
        """

        try:
            # Full path to uvcdynctrl needed.
            control_name = self.control_names[control]
            subproc_call(
                [
                    "/usr/bin/uvcdynctrl",
                    "-d", self.device_name,
                    "-s", control_name, value.__str__()
                ]
            )

        except SubprocessError or KeyError or FileNotFoundError as err:
            Camera.logger.error(f'Error while setting up {control} with value: `{value}`')
            Camera.logger.error(f'Error message: {err.__str__()}')

    def get_control_value(self, control: AnyStr) -> bool or int:
        """
        Call uvcdynctrl in a subprocess to get the current value of a control.

        :param control: Control name/type (e.g., "zoom").
        :type control: str
        :return: The control value (as an integer for controls that can take on
            a range of discrete values, or as a boolean for controls that can
            be toggled on/off).
        :rtype: int | str
        """

        try:
            control_name = self.control_names[control]
            value = check_output(
                [
                    "/usr/bin/uvcdynctrl",
                    "-d", self.device_name,
                    "-g", control_name
                ]
            )
            value = int(value.decode("utf-8").strip())

            # Return a boolean for autofocus and autoexposure; otherwise, return raw int.
            # Options are 1 (manual mode) and 3 (aperture priority mode).
            if control == "autofocus":
                return value == 1

            elif control == "autoexposure":
                return value == 3

            return value

        except SubprocessError or KeyError or FileNotFoundError as err:
            Camera.logger.error(f'Error while getting up {control}')
            Camera.logger.error(f'Error message: {err.__str__()}')

            return 0
