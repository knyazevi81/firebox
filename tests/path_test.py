import requests 
import json
import random

def get_random_test_url(
    data: list[dict[str | str]], 
    length: int  # Изменено имя параметра
) -> list[dict[str | str]]:
    """
    Get a random test URL from the list of URLs.
    
    Args:
        data (list[dict[str | str]]): List of dictionaries containing test URLs.
        length (int): Number of random URLs to select.

    Returns:
        list[dict[str | str]]: List of selected random URLs.
    """
    if length > len(data):  # Используем новое имя параметра
        raise ValueError("Length exceeds the number of available URLs.")
    
    return random.sample(data, min(1000, length))

def test_by_ursl(
    host: str, 
    test_urls_file: str,
    len_test: int = 1000
) -> None:
    with open(test_urls_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    tests = get_random_test_url(data, len_test)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    for i in range(len(tests)):
        url = host + tests[i]["pattern"]
        response = requests.get(url, headers=headers)
        if response.status_code == 302 and tests[i]["type"] != "valid":
            print(f"Test {i} {tests[i]['pattern']}: Passed - {url}")

if __name__ == "__main__":
    test_by_ursl("http://localhost:8080/", "complete_clean.json", 1000)
