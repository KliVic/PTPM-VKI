import sys

from src.database import DatabaseRepository
from src.parser import ForumParser


def run(url: str, db_path: str = "quotes.db") -> None:
    parser = ForumParser.for_quotes_toscrape()
    print(f"Скачиваем: {url}")

    parsed = parser.parse_page(url)
    print(f"Извлечено записей: {len(parsed)}")

    for item in parsed[:5]:
        preview = item["message"][:60].replace("\n", " ")
        print(f"  id={item['id']:>3} | {item['name']:<20} | {preview}...")

    repo = DatabaseRepository(db_path)
    try:
        saved = parser.save_to_db(parsed, repo)
        print(f"Сохранено в БД ({db_path}): {saved}")
    finally:
        repo.close()


def main():
    # URL можно передать аргументом или ввести руками
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("URL: ").strip()

    if not url:
        print("URL не задан")
        return

    run(url)


if __name__ == "__main__":
    main()