import os
import unittest
from dotenv import dotenv_values

from src.aws_s3_helper.s3 import S3

class TestS3Operations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dotenv_values()
        cls.s3 = S3(
            aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
            aws_region=env["AWS_REGION"],
        )
        cls.bucket_name = "pruebas-files-novo"  # Reemplaza con el nombre de tu bucket
        cls.local_folder = "test_folder"
        cls.local_file = os.path.join(cls.local_folder, "test_file.txt")
        cls.s3_path = "test_folder/"

        # Crea la carpeta local y el archivo de prueba
        os.makedirs(cls.local_folder, exist_ok=True)
        with open(cls.local_file, "w") as f:
            f.write("Hola, esto es una prueba")

    def test_1_upload_folder(self):
        # Sube la carpeta al S3
        self.s3.upload_folder(self.bucket_name, self.local_folder, self.s3_path)

        # Verifica que el archivo subido existe en S3
        self.assertTrue(
            self.s3.list(self.bucket_name, self.s3_path)["files"] == ["test_file.txt"]
        )

    def test_2_read_file(self):
        # Lee el archivo directamente desde S3
        content = self.s3.read_file(self.bucket_name, self.s3_path + "test_file.txt")
        self.assertEqual(content, "Hola, esto es una prueba")

    def test_3_download_folder(self):
        # Elimina la carpeta local antes de descargar
        if os.path.exists(self.local_folder):
            os.system(f"rm -rf {self.local_folder}")

        # Descarga la carpeta desde S3
        self.s3.download_folder(self.bucket_name, self.s3_path, self.local_folder)

        # Verifica que la carpeta se haya descargado y el contenido sea correcto
        self.assertTrue(os.path.exists(self.local_file))
        with open(self.local_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Hola, esto es una prueba")

    def test_4_delete_folder(self):
        # Elimina la carpeta en S3
        self.s3.delete_folder(self.bucket_name, self.s3_path)

        # Verifica que la carpeta haya sido eliminada en S3
        self.assertTrue(self.s3_path not in self.s3.list(self.bucket_name)["folders"])

    @classmethod
    def tearDownClass(cls):
        # Limpia los archivos locales creados
        if os.path.exists(cls.local_folder):
            os.system(f"rm -rf {cls.local_folder}")


if __name__ == "__main__":
    unittest.main()
