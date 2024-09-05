import os

import boto3
from tqdm import tqdm

from botocore.exceptions import ClientError


def bucket_exists(client, bucket_name: str) -> bool:
    """
    Checks if an S3 bucket exists.

    Args:
        bucket_name (str): The name of the S3 bucket.

    Returns:
        bool: True if the bucket exists, False if it does not.

    Raises:
        Exception: If an error occurs when trying to verify the existence of the bucket.
    """
    try:
        client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            return False
        else:
            raise Exception(f"Error verifying the existence of the bucket: {e}")


def s3_path_exists(client, bucket_name: str, s3_path: str) -> bool:
    """
    Checks if a file or folder exists in the S3 bucket under the specified path.

    Args:
        bucket_name (str): The name of the S3 bucket.
        s3_path (str): The path to the file or folder in the bucket.

    Returns:
        bool: True if the file or folder exists, False if it does not exist.

    Raises:
        Exception: If an error occurs when trying to verify the existence of the file or folder.
    """
    if  s3_path.endswith("/"):  # Folder
        result = client.list_objects_v2(
            Bucket=bucket_name, Prefix=s3_path, Delimiter="/"
        )
        return "CommonPrefixes" in result or "Contents" in result
    else:  # File
        try:
            client.head_object(Bucket=bucket_name, Key=s3_path)
            return True
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                return False
            else:
                raise Exception(
                    f"Error verifying the existence of the file or folder: {e}"
                )


class S3:
    def __init__(
        self, aws_access_key_id: str, aws_secret_access_key: str, aws_region: str
    ):
        """
        AWS S3 client.

        Args:
            aws_access_key_id: The AWS access key.
            aws_secret_access_key: The AWS secret access key.
            aws_region: The AWS region.

        Raises:
            Exception: If the credentials or region are not well defined.
        """
        try:
            self.__client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
            )
            self.__region = aws_region
        except Exception as e:
            raise Exception("--- The S3 configuration is not correct --- ERROR", e)

    # ------------------------- List functions ---------------------------

    def list_buckets(self) -> list[str]:
        """
        Lists all the buckets in the AWS S3 account.

        Returns:
            list[str]: A list of bucket names.
        """
        try:
            response = self.__client.list_buckets()
            buckets = [bucket["Name"] for bucket in response["Buckets"]]
            return buckets
        except Exception as e:
            raise Exception("Failed to list buckets.", e)

    def list(self, bucket_name: str, prefix: str = "") -> dict[str, list[str]]:
        """
        Lists folders and files in an AWS S3 bucket under a specific prefix.

        Args:
            bucket_name (str): The name of the S3 bucket.
            prefix (str, optional): The prefix used to filter the objects in the bucket.
                                    Default is an empty string.

        returns:
            dict: A dictionary with two lists:
                  - 'folders': Names of folders found under the prefix (without the prefix or trailing slash).
                  - 'files': Names of the files found under the prefix (without the prefix).
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if len(prefix) > 0 and not s3_path_exists(self.__client, bucket_name, prefix):
            raise Exception(
                f"The path '{prefix}' does not exist in the bucket '{bucket_name}'."
            )

        # Removes the leading slash from the prefix if it exists
        if prefix.startswith("/"):
            prefix = prefix[1:]

        paginator = self.__client.get_paginator("list_objects_v2")
        operation_parameters: dict[str, str] = {
            "Bucket": bucket_name,
            "Prefix": prefix,
            "Delimiter": "/",
        }

        files: list[str] = []
        folders: list[str] = []

        for page in paginator.paginate(**operation_parameters):
            folders.extend(
                [
                    f["Prefix"][len(prefix) :].rstrip("/")
                    for f in page.get("CommonPrefixes", [])
                ]
            )
            files.extend([f["Key"][len(prefix) :] for f in page.get("Contents", [])])

        return {"folders": folders, "files": files}

    # ------------------------- File functions ---------------------------

    def read_file(self, bucket_name: str, s3_path: str) -> str:
        """
        Reads the contents of a file stored in an AWS S3 bucket without downloading it.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.

        Returns:
            str: The contents of the file as a string.

        Raises:
            Exception: If the bucket or file does not exist.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        response = self.__client.get_object(Bucket=bucket_name, Key=s3_path)
        content = response["Body"].read().decode("utf-8")
        return content

    def rename_file(self, bucket_name: str, old_s3_path: str, new_s3_path: str) -> None:
        """
        Renames a file in an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            old_s3_path (str): The current path of the file in the bucket.
            new_s3_path (str): The new path of the file in the bucket.

        Raises:
            Exception: If the bucket or file does not exist, or if the new path already exists.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, old_s3_path):
            raise Exception(f"The file '{old_s3_path}' does not exist in the bucket '{bucket_name}'.")

        if s3_path_exists(self.__client, bucket_name, new_s3_path):
            raise Exception(f"A file already exists at the new path '{new_s3_path}' in the bucket '{bucket_name}'.")

        # Copy the file to the new path
        self.__client.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': old_s3_path},
            Key=new_s3_path
        )

        # Delete the old file
        self.delete_file(bucket_name, old_s3_path)
    
    def download_file(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Download a file from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.
            local_path (str): The path where the downloaded file will be saved.
        """

        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        # Get file size in S3
        response = self.__client.head_object(Bucket=bucket_name, Key=s3_path)
        file_size = response["ContentLength"]

        # Configuring the progress bar
        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=os.path.basename(local_path),
        ) as progress_bar:

            def download_progress(bytes_transferred):
                progress_bar.update(bytes_transferred)

            self.__client.download_file(
                bucket_name, s3_path, local_path, Callback=download_progress
            )

    def upload_file(self, bucket_name: str, file_path: str, s3_path: str) -> None:
        """
        Upload a file to an AWS S3 bucket with a progress bar, checking if the file exists locally.

        Args:
            bucket_name (str): The name of the S3 bucket.
            file_path (str): The local path of the file to upload.
            s3_path (str): The path in the bucket where the file will be saved.

        Raises:
            Exception: If the bucket does not exist or the local file is not found.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"The file '{file_path}' does not exist on the local file system."
            )

        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        file_size = os.path.getsize(file_path)
        progress_bar = tqdm(
            total=file_size, unit="B", unit_scale=True, desc=f"Uploading {file_path}"
        )

        def upload_progress(chunk):
            progress_bar.update(chunk)

        self.__client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=s3_path,
            Callback=upload_progress,
        )

        progress_bar.close()
        
    def delete_file(self, bucket_name: str, s3_path: str) -> None:
        """
        Deletes a file from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the file in the bucket.

        Raises:
            Exception: If the bucket or file does not exist.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        self.__client.delete_object(Bucket=bucket_name, Key=s3_path)

    # ------------------------- Folder functions ---------------------------

    def download_folder(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Download a folder from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the folder in the bucket.
            local_path (str): The path where the downloaded folder will be saved.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The folder '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        # Create the local folder if it does not exist
        os.makedirs(local_path, exist_ok=True)
        objects = self.list(bucket_name, s3_path)
        total_items = len(objects["files"]) + len(objects["folders"])

        with tqdm(
            total=total_items,
            desc=f"Downloading folder: {local_path}",
        ) as overall_progress_bar:
            for file in objects["files"]:
                local_file_path = os.path.join(local_path, file)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                self.download_file(
                    bucket_name, os.path.join(s3_path, file), local_file_path
                )
                overall_progress_bar.update(1)

            for folder in objects["folders"]:
                self.download_folder(
                    bucket_name,
                    os.path.join(s3_path, folder) + "/",
                    os.path.join(local_path, folder) + "/",
                )
                overall_progress_bar.update(1)

    def upload_folder(self, bucket_name: str, folder_path: str, s3_path: str) -> None:
        """
        Upload an entire folder to an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            folder_path (str): The local path of the folder to upload.
            s3_path (str): The path in the bucket where the folder will be saved.

        Raises:
            Exception: If the bucket or local folder is not found.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not os.path.isdir(folder_path):
            raise FileNotFoundError(
                f"The folder '{folder_path}' does not exist on the local file system."
            )

        # Listar todos los archivos y carpetas en el directorio local
        total_files = sum(len(files) for _, _, files in os.walk(folder_path))
        total_folders = sum(len(dirs) for _, dirs, _ in os.walk(folder_path))
        total_items = total_files + total_folders

        with tqdm(
            total=total_items,
            desc=f"Uploading folder: {folder_path}",
        ) as overall_progress_bar:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, folder_path)
                    s3_file_path = os.path.join(s3_path, relative_path).replace(
                        "\\", "/"
                    )

                    self.upload_file(bucket_name, local_file_path, s3_file_path)
                    overall_progress_bar.update(1)

                for folder in dirs:
                    s3_folder_path = (
                        os.path.join(
                            s3_path,
                            os.path.relpath(os.path.join(root, folder), folder_path),
                        ).replace("\\", "/")
                        + "/"
                    )
                    self.__client.put_object(Bucket=bucket_name, Key=s3_folder_path)
                    overall_progress_bar.update(1)

    def delete_folder(self, bucket_name: str, s3_path: str) -> None:
        """
        Deletes a folder and all its contents from an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_path (str): The path to the folder in the bucket.

        Raises:
            Exception: If the bucket or folder does not exist.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"The folder '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        objects = self.list(bucket_name, s3_path)
        total_items = len(objects["files"]) + len(objects["folders"])

        with tqdm(
            total=total_items,
            desc=f"Removing folder: {s3_path}",
        ) as overall_progress_bar:
            for file in objects["files"]:
                self.delete_file(bucket_name, os.path.join(s3_path, file))
                overall_progress_bar.update(1)

            for folder in objects["folders"]:
                self.delete_folder(bucket_name, os.path.join(s3_path, folder) + "/")
                overall_progress_bar.update(1)
                
    def rename_folder(self, bucket_name: str, old_s3_path: str, new_s3_path: str) -> None:
        """
        Renames a folder in an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            old_s3_path (str): The current path of the folder in the bucket.
            new_s3_path (str): The new path of the folder in the bucket.

        Raises:
            Exception: If the bucket or folder does not exist, or if the new path already exists.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not s3_path_exists(self.__client, bucket_name, old_s3_path):
            raise Exception(f"The folder '{old_s3_path}' does not exist in the bucket '{bucket_name}'.")

        if s3_path_exists(self.__client, bucket_name, new_s3_path):
            raise Exception(f"A folder already exists at the new path '{new_s3_path}' in the bucket '{bucket_name}'.")

        objects = self.list(bucket_name, old_s3_path)
        total_items = len(objects["files"]) + len(objects["folders"])

        with tqdm(total=total_items, desc=f"Renaming folder: {old_s3_path} to {new_s3_path}") as overall_progress_bar:
            for file in objects["files"]:
                old_file_path = os.path.join(old_s3_path, file)
                new_file_path = os.path.join(new_s3_path, file)
                self.rename_file(bucket_name, old_file_path, new_file_path)
                overall_progress_bar.update(1)

            for folder in objects["folders"]:
                old_folder_path = os.path.join(old_s3_path, folder) + "/"
                new_folder_path = os.path.join(new_s3_path, folder) + "/"
                self.rename_folder(bucket_name, old_folder_path, new_folder_path)
                overall_progress_bar.update(1)

        # Optionally, delete the original folder's "directory marker"
        self.delete_file(bucket_name, old_s3_path)
         
    # ------------------------- Buckets functions ---------------------------
    
    def create_bucket(self, bucket_name: str) -> None:
        """
        Creates an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Raises:
            Exception: If the bucket already exists or if there is an error during creation.
        """
        if bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' already exists.")

        try:
            self.__client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.__region}
            )
        except self.__client.exceptions.BucketAlreadyExists:
            raise Exception(f"The bucket name '{bucket_name}' is already taken globally.")
        except self.__client.exceptions.BucketAlreadyOwnedByYou:
            raise Exception(f"You already own a bucket named '{bucket_name}'.")
        except Exception as e:
            raise Exception(f"Failed to create bucket '{bucket_name}'.", e)
        
    def delete_bucket(self, bucket_name: str) -> None:
        """
        Deletes an AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Raises:
            Exception: If the bucket does not exist or is not empty.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")
        
        objects = self.list(bucket_name)
        if objects["files"] or objects["folders"]:
            raise Exception(f"The bucket '{bucket_name}' is not empty.")
        
        self.__client.delete_bucket(Bucket=bucket_name)
    
    def rename_bucket(self, old_bucket_name: str, new_bucket_name: str) -> None:
        """
        Renames an AWS S3 bucket.

        Args:
            old_bucket_name (str): The name of the existing S3 bucket.
            new_bucket_name (str): The new name for the S3 bucket.

        Raises:
            Exception: If the old bucket does not exist, if the new bucket already exists,
                    or if there is an error during the process.
        """
        if not bucket_exists(self.__client, old_bucket_name):
            raise Exception(f"The bucket '{old_bucket_name}' does not exist.")

        if bucket_exists(self.__client, new_bucket_name):
            raise Exception(f"The bucket '{new_bucket_name}' already exists.")

        # Create the new bucket
        self.create_bucket(new_bucket_name)

        # Copy all objects from the old bucket to the new bucket
        objects = self.list(old_bucket_name)
        total_items = len(objects["files"]) + len(objects["folders"])

        with tqdm(total=total_items, desc=f"Renaming bucket: {old_bucket_name} to {new_bucket_name}") as progress_bar:
            # Copy files
            for file in objects["files"]:
                copy_source = {'Bucket': old_bucket_name, 'Key': file}
                self.__client.copy_object(
                    Bucket=new_bucket_name,
                    CopySource=copy_source,
                    Key=file
                )
                progress_bar.update(1)

            # Copy folders (as empty keys)
            for folder in objects["folders"]:
                folder_path = folder + "/" if not folder.endswith("/") else folder
                self.__client.put_object(Bucket=new_bucket_name, Key=folder_path)
                progress_bar.update(1)

        # Delete the old bucket and its contents
        self.delete_bucket(old_bucket_name)