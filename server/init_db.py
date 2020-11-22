"""Init database fot application"""
#!/usr/bin/env python3

import pathlib

from core import db

SQL_INIT = """
    CREATE TABLE test_results (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        dev_type VARCHAR,
        operator VARCHAR,
        dt       DATETIME,
        success  BOOL
    );
    CREATE INDEX test_results_operator_idx ON test_results(operator);
"""


def main():
    """Entry point"""

    db_path = pathlib.Path(db.PATH)
    print('> Preparing file directory...')
    db_path.parent.mkdir(exist_ok=True)

    if db_path.exists():
        if input(r'> Old db file exists, remove? (y/n) >>: ').strip().lower() == 'y':
            db_path.unlink()
        else:
            print('Abort!')
            return

    print('> Tables initialization...')
    with db.get_conn() as conn:
        conn.executescript(SQL_INIT)
    print('> Done...')


if __name__ == '__main__':
    main()
