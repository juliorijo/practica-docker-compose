import unittest
from unittest.mock import MagicMock, patch

import pymysql

from src.app import app, connect_db


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.connection = MagicMock()
        self.connection.__enter__.return_value = self.connection
        self.cursor = self.connection.cursor.return_value.__enter__.return_value
        self.db_patch = patch("src.app.connect_db", return_value=self.connection)
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)

    def test_home_records_and_displays_visit(self):
        self.cursor.fetchone.return_value = {"total": 7}
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hola Mundo", response.data)
        self.assertIn(b"<strong>7</strong>", response.data)
        self.cursor.execute.assert_any_call(
            "UPDATE visitas SET total = total + 1 WHERE id = 1"
        )
        self.connection.commit.assert_called_once()

    def test_home_reports_database_failure_without_leaking_credentials(self):
        with patch(
            "src.app.connect_db",
            side_effect=pymysql.OperationalError(1045, "secret-password"),
        ):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b"secret-password", response.data)

    def test_home_reports_missing_seed(self):
        self.cursor.fetchone.return_value = None
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.connection.commit.assert_not_called()

    def test_home_reports_query_failure(self):
        self.cursor.execute.side_effect = pymysql.ProgrammingError(1146, "missing table")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.connection.commit.assert_not_called()

    def test_health_checks_database_without_recording_visit(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})
        self.cursor.execute.assert_called_once_with("SELECT 1")
        self.connection.commit.assert_not_called()

    def test_health_reports_database_failure(self):
        self.cursor.execute.side_effect = pymysql.OperationalError(2006, "gone away")
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {"status": "error"})

    def test_connection_uses_environment_and_timeouts(self):
        environment = {
            "MYSQL_HOST": "db",
            "MYSQL_DATABASE": "hola_mundo",
            "MYSQL_USER": "hola",
            "MYSQL_PASSWORD": "test-only",
        }
        with patch.dict("os.environ", environment), patch(
            "src.app.pymysql.connect"
        ) as connect:
            connect_db()
        connect.assert_called_once_with(
            host="db",
            user="hola",
            password="test-only",
            database="hola_mundo",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
            read_timeout=5,
            write_timeout=5,
        )


if __name__ == "__main__":
    unittest.main()
