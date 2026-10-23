def test_database_connection(db):
    result = db.execute(
        __import__("sqlalchemy").text("SELECT 1")
    ).scalar()

    assert result == 1