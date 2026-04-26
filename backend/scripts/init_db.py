import asyncio
import os
from pathlib import Path

import aiomysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

SQL_FILE = Path(__file__).resolve().parents[1] / 'sql' / 'init_tables.sql'


def split_sql(content: str) -> list[str]:
  statements: list[str] = []
  chunk: list[str] = []

  for line in content.splitlines():
    stripped = line.strip()
    if not stripped:
      continue
    chunk.append(line)
    if stripped.endswith(';'):
      statement = '\n'.join(chunk).strip().rstrip(';')
      statements.append(statement)
      chunk = []

  if chunk:
    statements.append('\n'.join(chunk).strip().rstrip(';'))

  return statements


async def main() -> None:
  host = os.getenv('DB_HOST', 'localhost')
  port = int(os.getenv('DB_PORT', '3306'))
  user = os.getenv('DB_USER', 'root')
  password = os.getenv('DB_PASSWORD', '')

  sql_content = SQL_FILE.read_text(encoding='utf-8')
  statements = split_sql(sql_content)

  conn = await aiomysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    autocommit=True,
    connect_timeout=5,
  )

  try:
    async with conn.cursor() as cur:
      for statement in statements:
        await cur.execute(statement)

      await cur.execute('USE kids_explorer')
      await cur.execute('SHOW TABLES')
      rows = await cur.fetchall()
      print('SHOW TABLES =>', [row[0] for row in rows])
  finally:
    conn.close()


if __name__ == '__main__':
  asyncio.run(main())
