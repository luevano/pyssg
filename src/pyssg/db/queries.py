CREATE_FILES_TABLE = """
CREATE TABLE IF NOT EXISTS files(
    file_name TEXT NOT NULL PRIMARY KEY,
    create_time REAL NOT NULL,
    modify_time REAL NOT NULL DEFAULT 0.0,
    checksum TEXT NOT NULL,
    tags TUPLE NULL
)
"""

SELECT_FILE = """
SELECT * FROM files WHERE file_name = ?
"""

SELECT_FILE_ALL = """
SELECT * FROM files
"""

# when inserting, it is because the file is "just created",
#   no need to add modify_time
INSERT_FILE = """
INSERT INTO files(file_name, create_time, checksum, tags)
VALUES (?, ?, ?, ?)
RETURNING *
"""

# the create_time shouldn't be updated
UPDATE_FILE = """
UPDATE files
SET modify_time = ?,
    checksum = ?,
    tags = ?
WHERE file_name = ?
RETURNING *
"""

# the create_time shouldn't be updated
UPDATE_FILE_TAGS = """
UPDATE files
SET tags = ?
WHERE file_name = ?
RETURNING *
"""

