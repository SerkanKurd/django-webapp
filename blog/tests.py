from django.test import TestCase
from django.db import connection


class DatabaseConnectionTest(TestCase):

    def test_database_connection(self):
        """
        Veritabanı bağlantısının başarılı olup olmadığını test eder.
        """
        try:
            # PostgreSQL'e basit bir sorgu göndeririz.
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                self.assertEqual(row, (1,), "Veritabanı sorgusu başarısız.")

            # Eğer sorgu başarılı olursa, bu satır çalışır.
            self.assertTrue(True, "Veritabanı bağlantısı başarılı.")

        except Exception as e:
            self.fail(f"Veritabanı bağlantı hatası: {e}")
