import os

import boto3
from tqdm import tqdm
from utils_checks import bucket_exists, s3_path_exists


class S3:
    def __init__(
        self, aws_access_key_id: str, aws_secret_access_key: str, aws_region: str
    ):
        """
        Cliente de AWS S3.

        Args:
            aws_access_key_id: La clave de acceso de AWS.
            aws_secret_access_key: La clave secreta de acceso de AWS.
            aws_region: La región de AWS.

        Raises:
            KeyError: Si las credenciales o la región no están definidas en el archivo .env.
        """
        try:
            self.__client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
            )
        except Exception as e:
            raise Exception("--- La configuración del S3 no es correcta. --- ERROR", e)

    def list(self, bucket_name: str, prefix: str = "") -> dict[str, list[str]]:
        """
        Lista las carpetas y archivos en un bucket de AWS S3 bajo un prefijo específico.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            prefix (str, optional): El prefijo utilizado para filtrar los objetos en el bucket.
                                    Por defecto es una cadena vacía.

        Returns:
            dict: Un diccionario con dos listas:
                  - 'folders': Nombres de las carpetas encontradas bajo el prefijo (sin el prefijo ni la barra final).
                  - 'files': Nombres de los archivos encontrados bajo el prefijo (sin el prefijo).
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        if not s3_path_exists(self.__client, bucket_name, prefix):
            raise Exception(
                f"La ruta '{prefix}' no existe en el bucket '{bucket_name}'."
            )

        # Elimina la barra inicial del prefijo si existe
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

    def download_file(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Descarga un archivo de un bucket de AWS S3.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            s3_path (str): La ruta del archivo en el bucket.
            local_path (str): La ruta donde se guardará el archivo descargado.
        """

        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"El archivo '{s3_path}' no existe en el bucket '{bucket_name}'."
            )

        # Obtener el tamaño del archivo en S3
        response = self.__client.head_object(Bucket=bucket_name, Key=s3_path)
        file_size = response["ContentLength"]

        # Configurar la barra de progreso
        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=os.path.basename(local_path),
        ) as progress_bar:

            def download_progress(bytes_transferred):
                progress_bar.update(bytes_transferred)

            # Descargar el archivo con el gancho de progreso
            self.__client.download_file(
                bucket_name, s3_path, local_path, Callback=download_progress
            )

    def download_folder(self, bucket_name: str, s3_path: str, local_path: str) -> None:
        """
        Descarga una carpeta de un bucket de AWS S3.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            s3_path (str): La ruta de la carpeta en el bucket.
            local_path (str): La ruta donde se guardará la carpeta descargada.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"La carpeta '{s3_path}' no existe en el bucket '{bucket_name}'."
            )

        # Crea la carpeta local si no existe
        os.makedirs(local_path, exist_ok=True)
        objects = self.list(bucket_name, s3_path)
        total_items = len(objects["files"]) + len(objects["folders"])

        # Barra de progreso total para la descarga de la carpeta
        with tqdm(
            total=total_items,
            desc=f"Descargando carpeta {local_path}",
        ) as overall_progress_bar:
            # Descargar todos los archivos en la carpeta
            for file in objects["files"]:
                local_file_path = os.path.join(local_path, file)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                self.download_file(
                    bucket_name, os.path.join(s3_path, file), local_file_path
                )
                overall_progress_bar.update(1)

            # Descargar recursivamente todas las subcarpetas
            for folder in objects["folders"]:
                self.download_folder(
                    bucket_name,
                    os.path.join(s3_path, folder) + "/",
                    os.path.join(local_path, folder) + "/",
                )
                overall_progress_bar.update(1)

    def read_file(self, bucket_name: str, s3_path: str) -> str:
        """
        Lee el contenido de un archivo almacenado en un bucket de AWS S3 sin descargarlo.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            s3_path (str): La ruta del archivo en el bucket.

        Returns:
            str: El contenido del archivo como una cadena de texto.

        Raises:
            Exception: Si el bucket o el archivo no existen.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"El archivo '{s3_path}' no existe en el bucket '{bucket_name}'."
            )

        response = self.__client.get_object(Bucket=bucket_name, Key=s3_path)
        content = response["Body"].read().decode("utf-8")
        return content

    def upload_file(self, bucket_name: str, file_path: str, s3_path: str) -> None:
        """
        Sube un archivo a un bucket de AWS S3 con una barra de progreso, verificando si el archivo existe localmente.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            file_path (str): La ruta local del archivo a subir.
            s3_path (str): La ruta en el bucket donde se guardará el archivo.

        Raises:
            Exception: Si el bucket no existe o el archivo local no se encuentra.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"El archivo '{file_path}' no existe en el sistema de archivos local."
            )

        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        file_size = os.path.getsize(file_path)
        progress_bar = tqdm(
            total=file_size, unit="B", unit_scale=True, desc=f"Subiendo {file_path}"
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

    def upload_folder(self, bucket_name: str, folder_path: str, s3_path: str) -> None:
        """
        Sube una carpeta completa a un bucket de AWS S3.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            folder_path (str): La ruta local de la carpeta a subir.
            s3_path (str): La ruta en el bucket donde se guardará la carpeta.

        Raises:
            Exception: Si el bucket o la carpeta local no se encuentran.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        if not os.path.isdir(folder_path):
            raise FileNotFoundError(
                f"La carpeta '{folder_path}' no existe en el sistema de archivos local."
            )

        # Listar todos los archivos y carpetas en el directorio local
        total_files = sum(len(files) for _, _, files in os.walk(folder_path))
        total_folders = sum(len(dirs) for _, dirs, _ in os.walk(folder_path))
        total_items = total_files + total_folders

        with tqdm(
            total=total_items,
            desc=f"Subiendo carpeta {folder_path}",
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

                # Crear carpetas en S3 (aunque no tienen contenido)
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

        print(
            f"Carpeta '{folder_path}' subida a '{s3_path}' en el bucket '{bucket_name}'."
        )

    def delete_file(self, bucket_name: str, s3_path: str) -> None:
        """
        Elimina un archivo de un bucket de AWS S3.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            s3_path (str): La ruta del archivo en el bucket.

        Raises:
            Exception: Si el bucket o el archivo no existen.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"El archivo '{s3_path}' no existe en el bucket '{bucket_name}'."
            )

        self.__client.delete_object(Bucket=bucket_name, Key=s3_path)
        print(f"Archivo '{s3_path}' eliminado del bucket '{bucket_name}'.")

    def delete_folder(self, bucket_name: str, s3_path: str) -> None:
        """
        Elimina una carpeta y todo su contenido de un bucket de AWS S3.

        Args:
            bucket_name (str): El nombre del bucket de S3.
            s3_path (str): La ruta de la carpeta en el bucket.

        Raises:
            Exception: Si el bucket o la carpeta no existen.
        """
        if not bucket_exists(self.__client, bucket_name):
            raise Exception(f"El bucket '{bucket_name}' no existe.")

        if not s3_path_exists(self.__client, bucket_name, s3_path):
            raise Exception(
                f"La carpeta '{s3_path}' no existe en el bucket '{bucket_name}'."
            )

        # Lista todos los archivos y carpetas dentro de la carpeta a eliminar
        objects = self.list(bucket_name, s3_path)
        total_items = len(objects["files"]) + len(objects["folders"])

        with tqdm(
            total=total_items,
            desc=f"Eliminando carpeta {s3_path}",
        ) as overall_progress_bar:
            # Eliminar todos los archivos en la carpeta
            for file in objects["files"]:
                self.delete_file(bucket_name, os.path.join(s3_path, file))
                overall_progress_bar.update(1)

            # Eliminar recursivamente todas las subcarpetas
            for folder in objects["folders"]:
                self.delete_folder(bucket_name, os.path.join(s3_path, folder) + "/")
                overall_progress_bar.update(1)

        # Finalmente, elimina la carpeta principal
        self.__client.delete_object(Bucket=bucket_name, Key=s3_path.rstrip("/") + "/")
        print(
            f"Carpeta '{s3_path}' y su contenido eliminados del bucket '{bucket_name}'."
        )