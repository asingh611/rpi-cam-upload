import unittest

import camera_constants
import image_write
import os
from camera_constants import *


class ImageWriteMethodsTest(unittest.TestCase):
    def test_folder_creation(self):
        image_write.create_local_write_folder()
        folders_created = False
        date_folder_path = os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER)
        difference_path = os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, "difference")
        lores_path = os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, "lores")
        nodetection_path = os.path.join(LOCAL_OUTPUT_FOLDER, LOCAL_OUTPUT_SUBFOLDER, "nodetection")
        if os.path.exists(date_folder_path) and os.path.exists(difference_path) \
                and os.path.exists(lores_path) and os.path.exists(nodetection_path):
            folders_created = True
        self.assertEqual(folders_created, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
