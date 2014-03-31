# -*- coding: utf-8 -*-

import os
import re

import tesseract


class OCR:
    def __init__(self):
        api = tesseract.TessBaseAPI()

        # For some reason, passing the path to Init() was not working,
        # but setting the environment variable seems to be a workaround.
        this_directory = os.path.dirname(os.path.realpath(__file__))
        os.putenv("TESSDATA_PREFIX", this_directory)

        api.Init(".", "ibge", tesseract.OEM_DEFAULT)

        api.SetPageSegMode(tesseract.PSM_AUTO)
        api.SetVariable("tessedit_char_whitelist", "-0123456789°'\"")
        api.SetVariable("chs_leading_punct", "-")
        api.SetVariable("numeric_punctuation", "-°'\"")

        self._api = api

    def GetDecimalDegrees(self, image):
        buffer = image.make_blob()

        tesseract.ProcessPagesBuffer(buffer, len(buffer), self._api)
        text = self._api.GetUTF8Text().replace(' ', '')
        coordinates = re.split("°|'|\"| ", text)[:3]

        # Do not accept low-quality OCRs, since this can cause
        # the image to be misplaced, which is worse than discarded.
        if self._api.MeanTextConf() < 60:
            return 0

        return self._ConvertToDecimalDegrees(coordinates)

    def _ConvertToDecimalDegrees(self, coordinates):
        try:
            degrees = float(coordinates[0])
            minutes = float(coordinates[1]) / 60
            seconds = float(coordinates[2]) / 3600
        except:
            return 0

        if (degrees < 0):
            minutes *= -1
            seconds *= -1

        return degrees + minutes + seconds
