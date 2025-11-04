import requests
import json
from colorama import init, Fore, Style
from typing import Optional, List, Dict

init(autoreset=True)

FAVOURITE_CURRENCIES = ["USD", "EUR", "RUB", "GBP"]

def get_currency_rate(currency_code: str) -> float:
    url = f"https://open.er-api.com/v6/latest/{currency_code}"
    resp = requests.get(url, timeout=60)
    if resp.status_code != 200:
        print(f"Failed to get currency rate for {currency_code}")
        return None

    return resp.json()

def save_to_file(data: dict):
    with open("currency_rate.json", "w") as file:
        json.dump(data, file)
    print(f"Данные сохранены в currency_rate.json")

def update_currency_rate():
    all_data = {}
    for currency in FAVOURITE_CURRENCIES:
        rate = get_currency_rate(currency)
        all_data[currency] = rate
    save_to_file(all_data)
    print(f"Данные обновлены")

def read_from_file():
    with open("currency_rate.json", "r", encoding="utf-8") as file:
        return json.load(file)

def get_all_available_currencies() -> List[str]:
    """Получает список всех доступных валют из файла"""
    data = read_from_file()
    currencies = set()
    for base_currency, currency_data in data.items():
        if "rates" in currency_data:
            currencies.update(currency_data["rates"].keys())
    return sorted(list(currencies))

def find_base_currency_for_pair(from_currency: str, to_currency: str) -> Optional[str]:
    """Находит базовую валюту, которая содержит оба курса"""
    data = read_from_file()
    for base_currency, currency_data in data.items():
        if "rates" in currency_data:
            rates = currency_data["rates"]
            if from_currency in rates and to_currency in rates:
                return base_currency
    return None

def convert_currency(from_currency: str, to_currency: str, amount: float) -> Optional[float]:
    """Конвертирует сумму из одной валюты в другую"""
    if from_currency == to_currency:
        return amount
    
    data = read_from_file()
    
    # Пытаемся найти базовую валюту, которая содержит оба курса
    base_currency = find_base_currency_for_pair(from_currency, to_currency)
    
    if base_currency:
        rates = data[base_currency]["rates"]
        if from_currency in rates and to_currency in rates:
            # Конвертируем через базовую валюту
            from_rate = rates[from_currency]  # курс from_currency к base_currency
            to_rate = rates[to_currency]      # курс to_currency к base_currency
            
            # Конвертируем: amount * (to_rate / from_rate)
            result = amount * (to_rate / from_rate)
            return result
    
    # Если не нашли прямую базовую валюту, конвертируем через USD
    if "USD" in data and "rates" in data["USD"]:
        usd_rates = data["USD"]["rates"]
        if from_currency in usd_rates and to_currency in usd_rates:
            from_rate = usd_rates[from_currency]
            to_rate = usd_rates[to_currency]
            result = amount * (to_rate / from_rate)
            return result
    
    return None

def display_currency_list(currencies: List[str], per_row: int = 5):
    """Выводит список валют в виде таблицы"""
    print(f"\n{Fore.CYAN}Доступные валюты:{Style.RESET_ALL}")
    for i, currency in enumerate(currencies, 1):
        end_char = "\n" if i % per_row == 0 else "  "
        print(f"{Fore.YELLOW}{currency:6}{Style.RESET_ALL}", end=end_char)
    if len(currencies) % per_row != 0:
        print()

def run_currency_converter():
    """Интерактивный интерфейс для конвертации валют"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"{'='*20} КОНВЕРТЕР ВАЛЮТ {'='*20}")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    try:
        currencies = get_all_available_currencies()
        
        while True:
            display_currency_list(currencies)
            
            print(f"\n{Fore.MAGENTA}Введите исходную валюту (или 'q' для выхода):{Style.RESET_ALL} ", end="")
            from_currency = input().strip().upper()
            
            if from_currency.lower() == 'q':
                print(f"{Fore.GREEN}До свидания!{Style.RESET_ALL}")
                break
            
            if from_currency not in currencies:
                print(f"{Fore.RED}Ошибка: Валюта '{from_currency}' не найдена!{Style.RESET_ALL}\n")
                continue
            
            print(f"{Fore.MAGENTA}Введите целевую валюту:{Style.RESET_ALL} ", end="")
            to_currency = input().strip().upper()
            
            if to_currency not in currencies:
                print(f"{Fore.RED}Ошибка: Валюта '{to_currency}' не найдена!{Style.RESET_ALL}\n")
                continue
            
            print(f"{Fore.MAGENTA}Введите сумму для конвертации:{Style.RESET_ALL} ", end="")
            try:
                amount = float(input().strip())
            except ValueError:
                print(f"{Fore.RED}Ошибка: Некорректная сумма!{Style.RESET_ALL}\n")
                continue
            
            result = convert_currency(from_currency, to_currency, amount)
            
            if result is not None:
                print(f"\n{Fore.GREEN}{'='*60}")
                print(f"{Fore.YELLOW}{amount:,.2f} {from_currency} = {result:,.2f} {to_currency}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.RED}Ошибка: Не удалось конвертировать валюты!{Style.RESET_ALL}\n")
            
            print(f"{Fore.CYAN}Продолжить? (y/n):{Style.RESET_ALL} ", end="")
            if input().strip().lower() != 'y':
                print(f"{Fore.GREEN}До свидания!{Style.RESET_ALL}")
                break
            print()
    
    except FileNotFoundError:
        print(f"{Fore.RED}Ошибка: Файл currency_rate.json не найден!")
        print(f"Запустите программу с функцией update_currency_rate() для создания файла.{Style.RESET_ALL}")
    except json.JSONDecodeError:
        print(f"{Fore.RED}Ошибка: Неверный формат файла currency_rate.json!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        update_currency_rate()
    else:
        run_currency_converter()
    