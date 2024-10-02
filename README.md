# AWS S3 Helper Package 🇬🇧
![Python Version](https://img.shields.io/badge/python-3.8%2B-red)
![License](https://img.shields.io/badge/license-GPLv3-green)
[![Downloads](https://static.pepy.tech/badge/aws_s3_helper)](https://pepy.tech/project/aws_s3_helper)

## Description

`aws-s3-helper` is a Python utility that provides a simplified interface for interacting with AWS S3. It provides functions for uploading, downloading, reading, deleting, and renaming files and folders, as well as managing buckets.

## Features

-  **Listing Buckets, Folders, and Files:** List all the buckets in your S3 account, or list the contents of a specific folder in an S3 bucket.
- **File and Folder Upload:** Upload individual files or entire folders to an S3 bucket with a progress bar.
- **File and Folder Download:** Download individual files or folders from an S3 bucket with progress bar support.
- **Reading Files in S3:** Reads the contents of a file in S3 without the need to download the file.
- **Get Presigned URL for a File:** Generate a presigned URL for a file in an S3 bucket. This URL can be used to download the file without authentication.
- **File and Folder Deletion:** Deletes files or folders from an S3 bucket.
- **File and Folder Renaming:** Rename files or folders in an S3 bucket.
- **Bucket Management:** Create, delete, and rename S3 buckets.

## Installation

You can install the package directly from PyPi using pip:

```bash
pip3 install aws-s3-helper
```

### Dependencies
- *boto3*: AWS SDK for Python
- *tqdm*: Progress bar. OPTIONAL, only if you want to see logs.

```bash
pip3 install boto3 tqdm
```

## Usage
### Initial configuration
To get started, it is recommended to have an **.env** file in the root directory of your project with your AWS credentials:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_region
```

### Example of use

```Python
from dotenv import dotenv_values
from aws_s3_helper import S3

# Create an instance of the S3 class
env = dotenv_values()
s3 = S3(
    aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
    aws_region=env["AWS_REGION"],
    logging=True # Optional, set to True to enable logging. By default, it is set to False.
)

# Bucket name
bucket_name = "your-bucket"

# List all buckets in your S3 account
buckets = s3.list_buckets()
print("Buckets:", buckets)

# List the contents of a folder in S3
listing = s3.list(bucket_name, "path_in_s3")
print("Folders:", listing["folders"])
print("Files:", listing["files"])

# Upload a folder to S3
s3.upload_folder(bucket_name, "local_folder", "path_to_s3/")

# Read a file in S3 without downloading it
content = s3.read_file(bucket_name, "path_in_s3/file.txt")
print(content)

# Generate a presigned URL for a file in S3
presigned_url = s3.get_presigned_url_file(bucket_name, "path_in_s3/file.txt")
print(presigned_url)

# Download a folder from S3
s3.download_folder(bucket_name, "path_in_s3/", "local_folder/")

# Rename a file in S3
s3.rename_file(bucket_name, "path_in_s3/old_name.txt", "path_in_s3/new_name.txt")

# Rename a folder in S3
s3.rename_folder(bucket_name, "path_in_s3/old_folder/", "path_in_s3/new_folder/")

# Create a new bucket
s3.create_bucket("new-bucket")

# Rename a bucket
s3.rename_bucket("old-bucket-name", "new-bucket-name")

# Delete a folder in S3
s3.delete_folder(bucket_name, "path_in_s3/")

# Delete a bucket
s3.delete_bucket("bucket-to-delete")
```

### Running tests
To run the tests, follow these steps:

1.	Ensure you have a valid AWS configuration by setting up an .env file as described above.
2.	Install the necessary dependencies, which include unittest, boto3, and python-dotenv if they are not already installed:

    ```bash
    pip3 install boto3 python-dotenv
    ```
3.	Run the tests using the following command:

    ```bash
    python3 -m unittest discover -s test
    ```

This command will automatically discover and run all test cases in the test directory, checking the upload, download, read, delete, rename, and listing operations on S3, as well as bucket management functions.

## License
This project is licensed under the GNU GPLv3 license. See the LICENSE file for more details.

## Contact
For any question or suggestion, feel free to open an issue in the repository or contact me directly.

# Paquete AWS S3 Helper 🇪🇸

![Python Version](https://img.shields.io/badge/python-3.8%2B-red)
![License](https://img.shields.io/badge/license-GPLv3-green)
[![Downloads](https://static.pepy.tech/badge/aws_s3_helper)](https://pepy.tech/project/aws_s3_helper)

## Descripción

`aws-s3-helper` es una utilidad de Python que proporciona una interfaz simplificada para interactuar con AWS S3. Ofrece funciones para subir, descargar, leer, y eliminar archivos y carpetas.

## Características

- **Subida de Archivos y Carpetas:** Sube archivos individuales o carpetas enteras a un bucket de S3 con una barra de progreso.
- **Descarga de Archivos y Carpetas:** Descarga archivos individuales o carpetas desde un bucket de S3 con soporte de barra de progreso.
- **Lectura de Archivos en S3:** Lee el contenido de un archivo en S3 sin necesidad de descargarlo.
- **Generación de URL de Pre-Autorizada para un archivo:** Genera una URL de pre-autorizada para un archivo en un bucket de S3. Esta URL se puede utilizar para descargar el archivo sin autenticación.
- **Eliminación de Archivos y Carpetas:** Elimina archivos o carpetas de un bucket de S3.
- **Gestión de Buckets:** Crea, elimina, renombra y lista buckets de S3.
- **Listar Buckets, Carpetas y Archivos:** Lista todos los buckets en tu cuenta de S3, o lista el contenido de una carpeta específica en un bucket de S3.

## Instalación

Puedes instalar el paquete directamente desde PyPi usando pip:

```bash
pip3 install aws-s3-helper
```

### Dependencias
- *boto3*: AWS SDK para Python
- *tqdm*: Barra de progreso. OPCIONAL, solo si deseas ver los logs.

```bash
pip3 install boto3 tqdm
```

## Uso
### Configuración Inicial
Para comenzar, es recomendable tener un archivo **.env** en el directorio raíz de tu proyecto con tus credenciales de AWS:

```
AWS_ACCESS_KEY_ID=tu_access_key_id
AWS_SECRET_ACCESS_KEY=tu_secret_access_key
AWS_REGION=tu_region
```

### Ejemplo de uso

```Python
from dotenv import dotenv_values
from aws_s3_helper import S3

# Crea una instancia de la clase S3
env = dotenv_values()
s3 = S3(
    aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
    aws_region=env["AWS_REGION"],
    logging=True # Opcional, establece a True para habilitar el registro. Por defecto, se establece a False.
)

# Nombre del bucket
bucket_name = "tu-bucket"

# Listar todos los buckets en tu cuenta de S3
buckets = s3.list_buckets()
print("Buckets:", buckets)

# Listar el contenido de una carpeta en S3
listado = s3.list(bucket_name, "ruta_en_s3")
print("Carpetas:", listado["folders"])
print("Archivos:", listado["files"])

# Subir una carpeta a S3
s3.upload_folder(bucket_name, "carpeta_local", "ruta_en_s3/")

# Leer un archivo en S3 sin descargarlo
contenido = s3.read_file(bucket_name, "ruta_en_s3/archivo.txt")
print(contenido)

# Generar una URL de pre-autorizada para un archivo en S3
presigned_url = s3.get_presigned_url_file(bucket_name, "ruta_en_s3/archivo.txt")
print(presigned_url)

# Descargar una carpeta desde S3
s3.download_folder(bucket_name, "ruta_en_s3/", "carpeta_local/")

# Renombrar un archivo en S3
s3.rename_file(bucket_name, "ruta_en_s3/viejo_nombre.txt", "ruta_en_s3/nuevo_nombre.txt")

# Renombrar una carpeta en S3
s3.rename_folder(bucket_name, "ruta_en_s3/carpeta_vieja/", "ruta_en_s3/carpeta_nueva/")

# Crear un nuevo bucket
s3.create_bucket("nuevo-bucket")

# Renombrar un bucket
s3.rename_bucket("bucket-viejo-nombre", "bucket-nuevo-nombre")

# Eliminar una carpeta en S3
s3.delete_folder(bucket_name, "ruta_en_s3/")

# Eliminar un bucket
s3.delete_bucket("bucket-a-eliminar")
```

### Ejecución de test
Para ejecutar los tests, sigue estos pasos:

1.	Asegúrate de que tienes una configuración de AWS válida mediante la creación de un archivo .env como se describe anteriormente.

2.	Instala las dependencias necesarias, que incluyen unittest, boto3, y python-dotenv si aún no están instaladas:

    ```bash
    pip3 install boto3 python-dotenv
    ```
3.	Ejecuta los tests con el siguiente comando:

    ```bash
    python3 -m unittest discover -s test
    ```

Este comando descubrirá y ejecutará automáticamente todos los casos de prueba en el directorio test, comprobando las operaciones de subida, descarga, lectura, eliminación, renombrado y listado en S3, así como las funciones de gestión de buckets.

## Licencia
Este proyecto está licenciado bajo la licencia GNU GPLv3. Consulta el archivo LICENSE para más detalles.

## Contacto
Para cualquier consulta o sugerencia, no dudes en abrir un issue en el repositorio o contactarme directamente.
