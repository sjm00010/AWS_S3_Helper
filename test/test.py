import os
import unittest
from dotenv import dotenv_values

from aws_s3_helper import S3

class TestS3Operations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dotenv_values()
        cls.s3 = S3(
            aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
            aws_region=env["AWS_REGION"],
        )
        cls.bucket_name = "bucket-test"
        cls.new_bucket_name = "bucket-test-renamed"
        cls.local_folder = "test_folder"
        cls.file_name = "test_file.txt"
        cls.s3_path = "test_folder/"
        cls.new_s3_path = "test_folder_renamed/"
        cls.text_file = "Hello, this is a test"
        cls.local_file_path = os.path.join(cls.local_folder, cls.file_name)

        # Create local folder and test file
        os.makedirs(cls.local_folder, exist_ok=True)
        with open(cls.local_file_path, "w") as f:
            f.write(cls.text_file)

    def test_0_create_bucket(self):
        # Create a new bucket
        self.s3.create_bucket(self.bucket_name)
        buckets = self.s3.list_buckets()
        self.assertIn(self.bucket_name, buckets)

    def test_1_upload_file(self):
        # Upload a single file to S3
        self.s3.upload_file(self.bucket_name, self.local_file_path, self.s3_path + self.file_name)

        # Check that the uploaded file exists in S3
        self.assertTrue(
            self.file_name in self.s3.list(self.bucket_name, self.s3_path)["files"]
        )

    def test_2_download_file(self):
        # Remove the local file before downloading
        if os.path.exists(self.local_file_path):
            os.remove(self.local_file_path)

        # Download the file from S3
        self.s3.download_file(self.bucket_name, self.s3_path + self.file_name, self.local_file_path)

        # Check that the file has been downloaded and the contents are correct
        self.assertTrue(os.path.exists(self.local_file_path))
        with open(self.local_file_path, "r") as f:
            content = f.read()
        self.assertEqual(content, self.text_file)

    def test_3_upload_folder(self):
        # Upload the folder to S3
        self.s3.upload_folder(self.bucket_name, self.local_folder, self.s3_path)

        # Check that the uploaded folder and its file exist in S3
        self.assertTrue(
            self.file_name in self.s3.list(self.bucket_name, self.s3_path)["files"]
        )

    def test_4_rename_file(self):
        # Rename the file in S3
        new_file_name = "test_file_renamed.txt"
        self.s3.rename_file(self.bucket_name, self.s3_path + self.file_name, self.s3_path + new_file_name)

        # Check that the old file does not exist and the new one does
        self.assertFalse(
            self.file_name in self.s3.list(self.bucket_name, self.s3_path)["files"]
        )
        self.assertTrue(
            new_file_name in self.s3.list(self.bucket_name, self.s3_path)["files"]
        )

        # Update the file name for subsequent tests
        self.file_name = new_file_name

    def test_5_rename_folder(self):
        # Rename the folder in S3
        self.s3.rename_folder(self.bucket_name, self.s3_path, self.new_s3_path)

        # Check that the old folder does not exist and the new one does
        self.assertFalse(
            self.s3_path in self.s3.list(self.bucket_name)["folders"]
        )
        self.assertTrue(
            self.new_s3_path in self.s3.list(self.bucket_name)["folders"]
        )

        # Update the S3 path for subsequent tests
        self.s3_path = self.new_s3_path

    def test_6_download_folder(self):
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

    def test_7_delete_folder(self):
        # Remove the folder in S3
        self.s3.delete_folder(self.bucket_name, self.s3_path)

        # Check that the folder has been deleted in S3
        self.assertTrue(self.s3_path not in self.s3.list(self.bucket_name)["folders"])

    def test_8_rename_bucket(self):
        # Rename the bucket
        self.s3.rename_bucket(self.bucket_name, self.new_bucket_name)
        
        # Check that the old bucket no longer exists and the new bucket does
        buckets = self.s3.list_buckets()
        self.assertNotIn(self.bucket_name, buckets)
        self.assertIn(self.new_bucket_name, buckets)

        # Update the bucket name for subsequent tests
        self.bucket_name = self.new_bucket_name

    def test_9_delete_bucket(self):
        # Delete the bucket created during the test
        self.s3.delete_bucket(self.bucket_name)
        buckets = self.s3.list_buckets()
        self.assertNotIn(self.bucket_name, buckets)

    @classmethod
    def tearDownClass(cls):
        # Cleans up the local files created
        if os.path.exists(cls.local_folder):
            os.system(f"rm -rf {cls.local_folder}")


if __name__ == "__main__":
    unittest.main()