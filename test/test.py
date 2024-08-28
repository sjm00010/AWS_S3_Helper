import os
import unittest
from dotenv import dotenv_values

from aws_s3_helper.s3 import S3

class TestS3Operations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dotenv_values()
        cls.s3 = S3(
            aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
            aws_region=env["AWS_REGION"],
        )
        cls.bucket_name = "pruebas-files-novo"
        cls.local_folder = "test_folder"
        cls.file_name = "test_file.txt"
        cls.s3_path = "test_folder/"
        cls.text_file = "Hello, this is a test"

        # Create local folder and test file
        os.makedirs(cls.local_folder, exist_ok=True)
        with open(os.path.join(cls.local_folder, cls.file_name), "w") as f:
            f.write(cls.text_file)

    def test_1_upload_folder(self):
        # Upload the folder to S3
        self.s3.upload_folder(self.bucket_name, self.local_folder, self.s3_path)

        # Check that the uploaded file exists in S3
        self.assertTrue(
            self.s3.list(self.bucket_name, self.s3_path)["files"] == [self.file_name]
        )

    def test_2_read_file(self):
        # Read the file directly from S3
        content = self.s3.read_file(self.bucket_name, self.s3_path + self.file_name)
        self.assertEqual(content, self.text_file)

    def test_3_download_folder(self):
        # Remove the local folder before downloading
        if os.path.exists(self.local_folder):
            os.system(f"rm -rf {self.local_folder}")

        # Download the folder from S3
        self.s3.download_folder(self.bucket_name, self.s3_path, self.local_folder)

        # Check that the folder has been downloaded and the contents are correct
        self.assertTrue(os.path.exists(os.path.join(self.local_folder, self.file_name)))
        with open(os.path.join(self.local_folder, self.file_name), "r") as f:
            content = f.read()
        self.assertEqual(content, self.text_file)

    def test_4_delete_folder(self):
        # Remove the folder in S3
        self.s3.delete_folder(self.bucket_name, self.s3_path)

        # Check that the folder has been deleted in S3
        self.assertTrue(self.s3_path not in self.s3.list(self.bucket_name)["folders"])

    @classmethod
    def tearDownClass(cls):
        # Cleans up the local files created
        if os.path.exists(os.path.join(cls.local_folder, cls.file_name)):
            os.system(f"rm -rf {cls.local_folder}")


if __name__ == "__main__":
    unittest.main()
