import json
from typing import Any, Dict, List, Optional

import requests
from colorama import Fore, Style, init as colorama_init


def _safe_get(dct: Dict[str, Any], path: List[str], default: str = "—") -> Any:
    cur: Any = dct
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def _format_list(values: Optional[List[Any]]) -> str:
    if not values:
        return "—"
    return ", ".join(str(v) for v in values)


def _format_currencies(currencies: Optional[Dict[str, Any]]) -> str:
    if not currencies:
        return "—"
    parts: List[str] = []
    for code, info in currencies.items():
        name = info.get("name") or ""
        symbol = info.get("symbol") or ""
        if name and symbol:
            parts.append(f"{code} ({name}, {symbol})")
        elif name:
            parts.append(f"{code} ({name})")
        else:
            parts.append(code)
    return ", ".join(parts) if parts else "—"


def _format_languages(languages: Optional[Dict[str, Any]]) -> str:
    if not languages:
        return "—"
    return ", ".join(str(name) for name in languages.values())


def _print_country_info(country: Dict[str, Any]) -> None:
    title_color = Fore.CYAN + Style.BRIGHT
    label_color = Fore.YELLOW + Style.BRIGHT
    value_color = Fore.WHITE + Style.NORMAL
    section_color = Fore.MAGENTA + Style.BRIGHT

    common_name = _safe_get(country, ["name", "common"]) or "—"
    official_name = _safe_get(country, ["name", "official"]) or "—"
    flag_emoji = country.get("flag", "")

    print(section_color + "\n==== Информация о стране ====" + Style.RESET_ALL)
    print(title_color + f"{flag_emoji} {common_name}" + Style.RESET_ALL)
    print(label_color + "Официальное название: " + value_color + f"{official_name}" + Style.RESET_ALL)

    capital = _format_list(country.get("capital"))
    region = country.get("region") or "—"
    subregion = country.get("subregion") or "—"
    timezones = _format_list(country.get("timezones"))

    print(label_color + "Столица: " + value_color + f"{capital}" + Style.RESET_ALL)
    print(label_color + "Регион / Подрегион: " + value_color + f"{region} / {subregion}" + Style.RESET_ALL)
    print(label_color + "Часовые пояса: " + value_color + f"{timezones}" + Style.RESET_ALL)

    population = country.get("population")
    area = country.get("area")
    print(label_color + "Население: " + value_color + f"{population if population is not None else '—'}" + Style.RESET_ALL)
    print(label_color + "Площадь (км²): " + value_color + f"{area if area is not None else '—'}" + Style.RESET_ALL)

    borders = _format_list(country.get("borders"))
    print(label_color + "Соседние страны (коды): " + value_color + f"{borders}" + Style.RESET_ALL)

    currencies = _format_currencies(country.get("currencies"))
    languages = _format_languages(country.get("languages"))
    print(label_color + "Валюта: " + value_color + f"{currencies}" + Style.RESET_ALL)
    print(label_color + "Языки: " + value_color + f"{languages}" + Style.RESET_ALL)

    maps = country.get("maps") or {}
    google_maps = maps.get("googleMaps") or "—"
    osm = maps.get("openStreetMaps") or "—"
    print(label_color + "Карты (Google): " + Fore.BLUE + f"{google_maps}" + Style.RESET_ALL)
    print(label_color + "Карты (OSM): " + Fore.BLUE + f"{osm}" + Style.RESET_ALL)

    flags = country.get("flags") or {}
    flag_png = flags.get("png") or "—"
    flag_svg = flags.get("svg") or "—"
    print(label_color + "Флаг (PNG): " + Fore.BLUE + f"{flag_png}" + Style.RESET_ALL)
    print(label_color + "Флаг (SVG): " + Fore.BLUE + f"{flag_svg}" + Style.RESET_ALL)

    coat = country.get("coatOfArms") or {}
    coat_png = coat.get("png") or "—"
    coat_svg = coat.get("svg") or "—"
    if coat_png != "—" or coat_svg != "—":
        print(label_color + "Герб (PNG): " + Fore.BLUE + f"{coat_png}" + Style.RESET_ALL)
        print(label_color + "Герб (SVG): " + Fore.BLUE + f"{coat_svg}" + Style.RESET_ALL)


def fetch_country_info(country: str, timeout_seconds: int = 60) -> List[Dict[str, Any]]:
    url = f"https://restcountries.com/v3.1/name/{country}"
    resp = requests.get(url, timeout=timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise ValueError("Неожиданный формат ответа: ожидался список")
    return data


def run_country_cli() -> None:
    colorama_init(autoreset=True)
    print(Fore.GREEN + Style.BRIGHT + "Информация о стране (restcountries)" + Style.RESET_ALL)
    country = input("Введите название страны: ").strip()
    if not country:
        print(Fore.RED + "Страна не может быть пустой." + Style.RESET_ALL)
        return
    try:
        data = fetch_country_info(country)
    except requests.HTTPError as exc:
        color = Fore.RED + Style.BRIGHT
        print(color + f"HTTP ошибка: {exc}" + Style.RESET_ALL)
        return
    except requests.RequestException as exc:
        print(Fore.RED + f"Сетевая ошибка: {exc}" + Style.RESET_ALL)
        return
    except ValueError as exc:
        print(Fore.RED + f"Ошибка формата данных: {exc}" + Style.RESET_ALL)
        return

    if not data:
        print(Fore.YELLOW + "Данные не найдены." + Style.RESET_ALL)
        return

    # В ответе может быть несколько стран (совпадения). Выведем каждую.
    for idx, c in enumerate(data, start=1):
        if len(data) > 1:
            print(Fore.CYAN + Style.BRIGHT + f"\n— Совпадение #{idx} —" + Style.RESET_ALL)
        _print_country_info(c)


if __name__ == "__main__":
    run_country_cli()


