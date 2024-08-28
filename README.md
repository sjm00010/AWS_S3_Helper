# AWS S3 Helper Package 🇬🇧
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Description

`aws-s3-helper` is a Python utility that provides a simplified interface for interacting with AWS S3. It provides functions for uploading, downloading, reading, and deleting files and folders.

## Features

- File and Folder Upload:** Upload individual files or entire folders to an S3 bucket with a progress bar.
- File and Folder Download:** Download individual files or folders from an S3 bucket with progress bar support.
- Reading Files in S3:** Reads the contents of a file in S3 without the need to download the file.
- File and Folder Deletion:** Deletes files or folders from an S3 bucket.
- Existence Check:** Checks the existence of buckets and objects in S3.

## Installation

You can install the package directly from PyPi using pip:

```bash
pip3 install aws-s3-utilities
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
from aws_s3_helper.s3 import S3

### Create an instance of the S3 class
env = dotenv_values()
s3 = S3(
    aws_access_key_id=env[“AWS_ACCESS_KEY_ID”],
    aws_secret_access_key=env[“AWS_SECRET_ACCESS_KEY”],
    aws_region=env[“AWS_REGION”],
)

# bucket name
bucket_name = “tu-bucket”

# List the contents of a folder in S3
listing = s3.list(bucket_name, “path_in_s3”)
print(“Folders:”, list[“folders”])
print(“Files:”, list[“files”])

# Upload a folder to S3
s3.upload_folder(bucket_name, “local_folder”, “path_to_s3/”)

# Read a file in S3 without downloading it
content = s3.read_file(bucket_name, “path_in_s3/file.txt”)
print(content)

# Download a folder from S3
s3.download_folder(bucket_name, “path_in_s3/”, “local_folder/”)

# Delete a folder in S3
s3.delete_folder(bucket_name, “path_in_s3/”)
```

### Running tests
To run the tests, first make sure you have a valid AWS configuration (the tests use an environment variables file as discussed above). You can launch the tests using the VS Code utility or by running the following command:

```bash
python3 -m unittest discover -s test
```

This will run the tests that check the upload, download, read and delete operations on S3.

## License
This project is licensed under the GNU GPLv3 license. See the LICENSE file for more details.

## Contact
For any question or suggestion, feel free to open an issue in the repository or contact me directly.

# Paquete AWS S3 Helper 🇪🇸

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Descripción

`aws-s3-helper` es una utilidad de Python que proporciona una interfaz simplificada para interactuar con AWS S3. Ofrece funciones para subir, descargar, leer, y eliminar archivos y carpetas.

## Características

- **Subida de Archivos y Carpetas:** Sube archivos individuales o carpetas enteras a un bucket de S3 con una barra de progreso.
- **Descarga de Archivos y Carpetas:** Descarga archivos individuales o carpetas desde un bucket de S3 con soporte de barra de progreso.
- **Lectura de Archivos en S3:** Lee el contenido de un archivo en S3 sin necesidad de descargarlo.
- **Eliminación de Archivos y Carpetas:** Elimina archivos o carpetas de un bucket de S3.
- **Verificación de Existencia:** Comprueba la existencia de buckets y objetos en S3.

## Instalación

Puedes instalar el paquete directamente desde PyPi usando pip:

```bash
pip3 install aws-s3-utilities
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
from aws_s3_helper.s3 import S3

# Crea una instancia de la clase S3
env = dotenv_values()
s3 = S3(
    aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
    aws_region=env["AWS_REGION"],
)

# Nombre del bucket
bucket_name = "tu-bucket"

# Listar el contenido de una carpeta en S3
listado = s3.list(bucket_name, "ruta_en_s3")
print("Carpetas:", listado["folders"])
print("Archivos:", listado["files"])

# Subir una carpeta a S3
s3.upload_folder(bucket_name, "carpeta_local", "ruta_en_s3/")

# Leer un archivo en S3 sin descargarlo
contenido = s3.read_file(bucket_name, "ruta_en_s3/archivo.txt")
print(contenido)

# Descargar una carpeta desde S3
s3.download_folder(bucket_name, "ruta_en_s3/", "carpeta_local/")

# Eliminar una carpeta en S3
s3.delete_folder(bucket_name, "ruta_en_s3/")
```

### Ejecución de test
Para ejecutar los tests, primero asegúrate de que tienes una configuración de AWS válida (los test utilizan un archivo de variables de entorno como el comentado anteriormente). Puedes lanzar los test mediante la utilidad de VS Code o mediante la ejecución del siguiente comando:

```bash
python3 -m unittest discover -s test
```

Esto ejecutará los tests que comprueban las operaciones de subida, descarga, lectura y eliminación en S3.

## Licencia
Este proyecto está licenciado bajo la licencia GNU GPLv3. Consulta el archivo LICENSE para más detalles.

## Contacto
Para cualquier consulta o sugerencia, no dudes en abrir un issue en el repositorio o contactarme directamente.