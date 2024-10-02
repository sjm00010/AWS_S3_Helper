import os

import boto3
from tqdm import tqdm

from aws_s3_helper.interface import S3Interface
from aws_s3_helper.s3_base import S3Base

class S3WithLogs(S3Interface, S3Base):
    def __init__(
        self, aws_access_key_id: str, aws_secret_access_key: str, aws_region: str
    ):
        """
        AWS S3 client with logging.

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
            
            super().__init__(self.__client)
        except Exception as e:
            raise Exception("--- The S3 configuration is not correct --- ERROR", e)

    # ------------------------- List functions ---------------------------

    def list_buckets(self) -> list[str]:
        try:
            response = self.__client.list_buckets()
            buckets = [bucket["Name"] for bucket in response["Buckets"]]
            return buckets
        except Exception as e:
            raise Exception("Failed to list buckets.", e)

    def list(self, bucket_name: str, prefix: str = "") -> dict[str, list[str]]:
        if prefix != "":
            # Removes the leading slash from the prefix if it exists
            if prefix.startswith("/"):
                prefix = prefix[1:]
        
            # Add a trailing slash to the prefix if it does not exist
            if not prefix.endswith("/"):
                prefix = prefix + "/"
            
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if len(prefix) > 0 and not self._s3_path_exists(bucket_name, prefix):
            raise Exception(
                f"The path '{prefix}' does not exist in the bucket '{bucket_name}'."
            )

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

    def read_file(self, bucket_name: str, s3_path: str, format: str | None = None) -> str:
        # Removes the leading slash from the s3_path if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
            
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not self._s3_path_exists(bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        response = self.__client.get_object(Bucket=bucket_name, Key=s3_path)

        if format is None:
            content = response["Body"].read()
        else:
            content = response["Body"].read().decode(format)
        return content

    def rename_file(self, bucket_name: str, old_s3_path: str, new_s3_path: str) -> None:
        # Removes the leading slash from the old_s3_path or new_s3_path if it exists
        if old_s3_path.startswith("/"):
            old_s3_path = old_s3_path[1:]
        if new_s3_path.startswith("/"):
            new_s3_path = new_s3_path[1:]
        
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not self._s3_path_exists(bucket_name, old_s3_path):
            raise Exception(f"The file '{old_s3_path}' does not exist in the bucket '{bucket_name}'.")

        if self._s3_path_exists(bucket_name, new_s3_path):
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
        # Removes the leading slash from the s3_path if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
        
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not self._s3_path_exists(bucket_name, s3_path):
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
            
    def get_presigned_url_file(self, bucket_name: str, s3_path: str) -> str:
        # Removes the leading slash from the s3_path if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
        
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")
        
        if not self._s3_path_exists(bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )
        
        response = self.__client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_path
            }
        )
        
        return response

    def upload_file(self, bucket_name: str, file_path: str, s3_path: str) -> None:
        # Removes the leading slash from the prefix if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"The file '{file_path}' does not exist on the local file system."
            )

        if not self._bucket_exists(bucket_name):
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
        # Removes the leading slash from the s3_path if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
        
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not self._s3_path_exists(bucket_name, s3_path):
            raise Exception(
                f"The file '{s3_path}' does not exist in the bucket '{bucket_name}'."
            )

        self.__client.delete_object(Bucket=bucket_name, Key=s3_path)

    # ------------------------- Folder functions ---------------------------

    def download_folder(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        # Removes the leading slash from the s3_path if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
        
        # Add a trailing slash to the s3_path if it does not exist
        if not s3_path.endswith("/"):
            s3_path = s3_path + "/"
            
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not self._s3_path_exists(bucket_name, s3_path):
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
        # Removes the leading slash from the s3_path if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
        
        # Add a trailing slash to the s3_path if it does not exist
        if not s3_path.endswith("/"):
            s3_path = s3_path + "/"
        
        if not self._bucket_exists(bucket_name):
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
        # Removes the leading slash from the s3_path if it exists
        if s3_path.startswith("/"):
            s3_path = s3_path[1:]
        
        # Add a trailing slash to the s3_path if it does not exist
        if not s3_path.endswith("/"):
            s3_path = s3_path + "/"
        
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not self._s3_path_exists(bucket_name, s3_path):
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
        # Removes the leading slash from the old_s3_path or new_s3_path if it exists
        if old_s3_path.startswith("/"):
            old_s3_path = old_s3_path[1:]
        if new_s3_path.startswith("/"):
            new_s3_path = new_s3_path[1:]
        
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")

        if not self._s3_path_exists(bucket_name, old_s3_path):
            raise Exception(f"The folder '{old_s3_path}' does not exist in the bucket '{bucket_name}'.")

        if self._s3_path_exists(bucket_name, new_s3_path):
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
        # Remove the leading slash from the bucket_name if it exists
        bucket_name.replace("/", "")
        
        if self._bucket_exists(bucket_name):
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
        # Remove the leading slash from the bucket_name if it exists
        bucket_name.replace("/", "")
        
        if not self._bucket_exists(bucket_name):
            raise Exception(f"The bucket '{bucket_name}' does not exist.")
        
        objects = self.list(bucket_name)
        if objects["files"] or objects["folders"]:
            raise Exception(f"The bucket '{bucket_name}' is not empty.")
        
        self.__client.delete_bucket(Bucket=bucket_name)
    
    def rename_bucket(self, old_bucket_name: str, new_bucket_name: str) -> None:
        # Remove the leading slash from the bucket_name if it exists
        old_bucket_name.replace("/", "")
        new_bucket_name.replace("/", "")
        
        if not self._bucket_exists(old_bucket_name):
            raise Exception(f"The bucket '{old_bucket_name}' does not exist.")

        if self._bucket_exists(new_bucket_name):
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