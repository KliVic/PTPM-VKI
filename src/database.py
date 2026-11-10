import sqlite3


class DatabaseRepository:
    MAX_NAME_LENGTH = 256
    MAX_MESSAGE_LENGTH = 8096

    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id      INTEGER PRIMARY KEY,
                name    TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    # чтение

    def get_by_id(self, comment_id: int):
        row = self.conn.execute(
            "SELECT id, name, message FROM comments WHERE id = ?",
            (comment_id,),
        ).fetchone()
        if row is None:
            return None
        return {"id": row["id"], "name": row["name"], "message": row["message"]}

    def get_by_name(self, username: str):
        rows = self.conn.execute(
            "SELECT id, name, message FROM comments WHERE name = ?",
            (username,),
        ).fetchall()
        return [
            {"id": r["id"], "name": r["name"], "message": r["message"]}
            for r in rows
        ]

    #запись

    def add(self, comment_id: int, username: str, message: str) -> bool:
        self._validate_id(comment_id)
        self._validate_name(username)
        self._validate_message(message)

        try:
            self.conn.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                (comment_id, username, message),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Комментарий с id={comment_id} уже существует")
        return True

    def update(self, comment_id: int, new_message: str) -> bool:
        self._validate_id(comment_id)
        self._validate_message(new_message)

        cur = self.conn.execute(
            "UPDATE comments SET message = ? WHERE id = ?",
            (new_message, comment_id),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        self._validate_id(comment_id)
        cur = self.conn.execute(
            "DELETE FROM comments WHERE id = ?",
            (comment_id,),
        )
        self.conn.commit()
        return cur.rowcount > 0

    #валидация

    @staticmethod
    def _validate_id(value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("comment_id должен быть int")

    @classmethod
    def _validate_name(cls, value):
        if not isinstance(value, str):
            raise ValueError("name должен быть строкой")
        if len(value) > cls.MAX_NAME_LENGTH:
            raise ValueError(
                f"name длиннее {cls.MAX_NAME_LENGTH} символов"
            )

    @classmethod
    def _validate_message(cls, value):
        if not isinstance(value, str):
            raise ValueError("message должен быть строкой")
        if len(value) > cls.MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"message длиннее {cls.MAX_MESSAGE_LENGTH} символов"
            )

    #утилиты

    def close(self):
        self.conn.close()