import json
import sys
from typing import Any, Dict, Optional

import requests


def _read_json_dict_input(prompt: str) -> Dict[str, Any]:
    """
    Просит ввести словарь в формате JSON. Пустая строка = пустой словарь.
    Примеры:
    {}
    {"Authorization": "Bearer TOKEN", "Accept": "application/json"}
    """
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return {}
        try:
            value = json.loads(raw)
            if isinstance(value, dict):
                return value
            print("Введите корректный JSON-объект ({} или {\"key\": \"value\"}).")
        except json.JSONDecodeError as exc:
            print(f"Ошибка парсинга JSON: {exc}. Попробуйте ещё раз или оставьте пусто.")


def _pretty_print_response(resp: requests.Response) -> None:
    print("\n=== Результат ===")
    print(f"Статус: {resp.status_code}")
    try:
        print(f"Время: {resp.elapsed.total_seconds():.3f} сек")
    except Exception:
        pass

    print("\nЗаголовки:")
    for k, v in resp.headers.items():
        print(f"  {k}: {v}")

    print("\nТело ответа:")
    content_type = resp.headers.get("Content-Type", "").lower()
    text: Optional[str] = None
    if "application/json" in content_type:
        try:
            parsed = resp.json()
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            return
        except Exception:
            # Падаем обратно к тексту
            text = resp.text
    else:
        text = resp.text

    if text is None:
        text = resp.text
    print(text)


def do_get_request() -> None:
    print("\n=== GET запрос ===")
    url = input("URL: ").strip()
    if not url:
        print("URL не может быть пустым.")
        return

    params = _read_json_dict_input(
        "Параметры query (JSON, пусто если нет), напр. {\"q\": \"test\"}: "
    )
    headers = _read_json_dict_input(
        "Заголовки (JSON, пусто если нет), напр. {\"Authorization\": \"Bearer ...\"}: "
    )

    try:
        resp = requests.get(url, params=params or None, headers=headers or None, timeout=60)
        _pretty_print_response(resp)
    except requests.RequestException as exc:
        print(f"Ошибка запроса: {exc}")

def make_get_country_request(country: str):
    url = f"https://restcountries.com/v3.1/name/{country}"
    resp = requests.get(url, timeout=60)
    _pretty_print_response(resp)



def do_post_request() -> None:
    print("\n=== POST запрос ===")
    url = input("URL: ").strip()
    if not url:
        print("URL не может быть пустым.")
        return

    headers = _read_json_dict_input(
        "Заголовки (JSON, пусто если нет), напр. {\"Content-Type\": \"application/json\"}: "
    )

    print("\nВыберите тип тела:")
    print("1) JSON (application/json)")
    print("2) form-data/x-www-form-urlencoded")
    body_mode = input("Ваш выбор (1/2, по умолчанию 1): ").strip() or "1"

    data: Optional[Dict[str, Any]] = None
    json_body: Optional[Any] = None

    if body_mode == "2":
        data = _read_json_dict_input(
            "Тело как словарь (JSON для формы), напр. {\"name\": \"John\"}: "
        )
    else:
        # По умолчанию JSON
        raw = input("Тело JSON (пусто = {}): ").strip()
        if raw == "":
            json_body = {}
        else:
            try:
                json_body = json.loads(raw)
            except json.JSONDecodeError as exc:
                print(f"Ошибка парсинга JSON: {exc}. Отправляем пустой объект.")
                json_body = {}

        # Добавим заголовок если отсутствует
        headers = {**headers}
        headers.setdefault("Content-Type", "application/json")

    try:
        resp = requests.post(
            url,
            headers=headers or None,
            json=json_body if json_body is not None else None,
            data=data if data is not None else None,
            timeout=60,
        )
        _pretty_print_response(resp)
    except requests.RequestException as exc:
        print(f"Ошибка запроса: {exc}")


def main() -> None:
    print("Консольный тестер HTTP (GET/POST)")
    while True:
        print("\nМеню:")
        print("1) Выполнить GET")
        print("2) Выполнить POST")
        print("3) Выбрать страну (restcountries)")
        print("q) Выход")
        choice = input("Ваш выбор: ").strip().lower()

        if choice == "1":
            do_get_request()
        elif choice == "2":
            do_post_request()
        elif choice == "3":
            country = input("Введите название страны (англ. или локально): ").strip()
            if country:
                make_get_country_request(country)
            else:
                print("Страна не может быть пустой.")
        elif choice in {"q", "quit", "exit"}:
            print("Выход.")
            break
        else:
            print("Неизвестная команда. Повторите ввод.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
        sys.exit(130)
