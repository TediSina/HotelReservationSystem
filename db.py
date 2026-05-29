"""MySQL connection and automatic database bootstrap helpers."""
from contextlib import contextmanager
from pathlib import Path
import re

import mysql.connector
from mysql.connector import Error, errorcode

from config import DB_CONFIG


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"

REQUIRED_TABLES = (
    "Klienti",
    "LlojiDhomes",
    "Dhoma",
    "Rezervimi",
    "Sherbim",
    "RezervimSherbim",
    "Fatura",
)
REQUIRED_VIEWS = (
    "v_rezervime_detajuara",
    "v_te_ardhurat_mujore",
    "v_shfrytezimi_dhomave",
)
REQUIRED_TRIGGERS = (
    "trg_rezervim_check_overlap",
    "trg_rezervim_status_dhomes",
)
REQUIRED_PROCEDURES = ("sp_gjenero_fature",)
SEED_TABLES = ("LlojiDhomes", "Dhoma", "Sherbim")


class Database:
    """Small singleton-style helper for the MySQL connection."""

    _conn = None
    _schema_checked = False

    @classmethod
    def get_connection(cls):
        if cls._conn is None or not cls._conn.is_connected():
            try:
                cls._conn = mysql.connector.connect(**DB_CONFIG)
            except Error as exc:
                if exc.errno != errorcode.ER_BAD_DB_ERROR:
                    raise
                cls._create_database_if_missing()
                cls._conn = mysql.connector.connect(**DB_CONFIG)

        if not cls._schema_checked:
            cls._ensure_schema(cls._conn)
        return cls._conn

    @classmethod
    def close(cls):
        if cls._conn and cls._conn.is_connected():
            cls._conn.close()
            cls._conn = None
            cls._schema_checked = False

    @classmethod
    @contextmanager
    def cursor(cls, dictionary=True):
        """Context manager for cursor handling with commit/rollback."""
        conn = cls.get_connection()
        cur = conn.cursor(dictionary=dictionary)
        try:
            yield cur
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cur.close()

    @classmethod
    def _ensure_schema(cls, conn):
        existing_tables = cls._existing_objects(
            conn,
            "information_schema.tables",
            "table_schema",
            "table_name",
            REQUIRED_TABLES,
        )
        missing_tables = cls._missing_names(REQUIRED_TABLES, existing_tables)
        if missing_tables:
            cls._run_sql_file(conn, "schema.sql", skip_database_commands=True)

        if cls._needs_seed(conn):
            cls._run_sql_file(
                conn,
                "seed.sql",
                skip_database_commands=True,
                insert_ignore=True,
            )

        if cls._supporting_objects_missing(conn):
            cls._run_sql_file(
                conn,
                "views_triggers_procs.sql",
                skip_database_commands=True,
            )

        conn.commit()
        cls._schema_checked = True

    @classmethod
    def _create_database_if_missing(cls):
        config = DB_CONFIG.copy()
        config.pop("database", None)
        config["autocommit"] = True

        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        try:
            db_name = cls._database_name()
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS {cls._quote_identifier(db_name)} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        finally:
            cur.close()
            conn.close()

    @classmethod
    def _database_name(cls):
        return DB_CONFIG.get("database") or "hotel_db"

    @staticmethod
    def _quote_identifier(identifier):
        return f"`{str(identifier).replace('`', '``')}`"

    @classmethod
    def _existing_objects(cls, conn, table, schema_column, name_column, names, extra_where=""):
        if not names:
            return set()

        placeholders = ", ".join(["%s"] * len(names))
        query = (
            f"SELECT {name_column} FROM {table} "
            f"WHERE {schema_column} = %s AND {name_column} IN ({placeholders})"
        )
        if extra_where:
            query += f" AND {extra_where}"

        cur = conn.cursor()
        try:
            cur.execute(query, (cls._database_name(), *names))
            return {str(row[0]).lower() for row in cur.fetchall()}
        finally:
            cur.close()

    @staticmethod
    def _missing_names(required, existing):
        return {name for name in required if name.lower() not in existing}

    @classmethod
    def _needs_seed(cls, conn):
        cur = conn.cursor()
        try:
            for table in SEED_TABLES:
                cur.execute(f"SELECT COUNT(*) FROM {cls._quote_identifier(table)}")
                if cur.fetchone()[0] == 0:
                    return True
            return False
        finally:
            cur.close()

    @classmethod
    def _supporting_objects_missing(cls, conn):
        views = cls._existing_objects(
            conn,
            "information_schema.views",
            "table_schema",
            "table_name",
            REQUIRED_VIEWS,
        )
        triggers = cls._existing_objects(
            conn,
            "information_schema.triggers",
            "trigger_schema",
            "trigger_name",
            REQUIRED_TRIGGERS,
        )
        procedures = cls._existing_objects(
            conn,
            "information_schema.routines",
            "routine_schema",
            "routine_name",
            REQUIRED_PROCEDURES,
            "routine_type = 'PROCEDURE'",
        )
        return (
            Database._missing_names(REQUIRED_VIEWS, views)
            or Database._missing_names(REQUIRED_TRIGGERS, triggers)
            or Database._missing_names(REQUIRED_PROCEDURES, procedures)
        )

    @classmethod
    def _run_sql_file(
        cls,
        conn,
        filename,
        *,
        skip_database_commands=False,
        insert_ignore=False,
    ):
        path = DATABASE_DIR / filename
        statements = cls._split_sql(path.read_text(encoding="utf-8-sig"))

        cur = conn.cursor()
        try:
            for statement in statements:
                if skip_database_commands and cls._is_database_command(statement):
                    continue

                statement = cls._make_idempotent(statement, insert_ignore)
                if cls._index_exists(conn, statement):
                    continue

                cur.execute(statement)
        finally:
            cur.close()

    @staticmethod
    def _split_sql(script):
        delimiter = ";"
        current = []
        statements = []

        for raw_line in script.splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            if stripped.upper().startswith("DELIMITER "):
                delimiter = stripped.split(None, 1)[1]
                continue

            current.append(raw_line)
            if stripped.endswith(delimiter):
                statement = "\n".join(current)
                statement = statement[: statement.rfind(delimiter)].strip()
                if statement:
                    statements.append(statement)
                current = []

        if current:
            statement = "\n".join(current).strip()
            if statement:
                statements.append(statement)

        return statements

    @staticmethod
    def _is_database_command(statement):
        command = statement.lstrip().upper()
        return command.startswith(("DROP DATABASE", "CREATE DATABASE", "USE "))

    @staticmethod
    def _make_idempotent(statement, insert_ignore=False):
        statement = re.sub(
            r"(?is)^\s*CREATE\s+TABLE\s+",
            "CREATE TABLE IF NOT EXISTS ",
            statement,
            count=1,
        )
        if insert_ignore:
            statement = re.sub(
                r"(?is)^\s*INSERT\s+INTO\s+",
                "INSERT IGNORE INTO ",
                statement,
                count=1,
            )
        return statement

    @classmethod
    def _index_exists(cls, conn, statement):
        match = re.match(
            r"(?is)^\s*CREATE\s+(?:UNIQUE\s+)?INDEX\s+`?([\w]+)`?\s+ON\s+`?([\w]+)`?",
            statement,
        )
        if not match:
            return False

        index_name, table_name = match.groups()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.statistics "
                "WHERE table_schema = %s AND table_name = %s AND index_name = %s",
                (cls._database_name(), table_name, index_name),
            )
            return cur.fetchone()[0] > 0
        finally:
            cur.close()


def test_connection():
    """Check if the application can connect to MySQL."""
    try:
        conn = Database.get_connection()
        if conn.is_connected():
            db_info = conn.get_server_info()
            return True, f"MySQL Server v{db_info}"
    except Error as e:
        return False, str(e)
    return False, "Lidhja deshtoi"
