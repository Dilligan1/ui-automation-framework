"""
Запуск нескольких наборов тестов параллельно.

Два уровня параллелизма:
  1. ProcessPoolExecutor — независимые наборы (smoke, regress) идут одновременно,
     каждый своим процессом pytest;
  2. pytest-xdist внутри набора — тесты набора распределяются по N браузерам.

Зачем так: наборы имеют разную длительность и разные требования к параллелизму.
Гонять всё одной командой с общим -n означает ждать самый долгий тест в общей
очереди; здесь короткий smoke отдаёт результат, не дожидаясь регрессии.

Запуск: python runner.py
"""

import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor


def run_tests(test_suite: str, num_threads: int) -> int:
    """Запустить один набор тестов и транслировать его вывод в консоль."""
    command = [
        "pytest",
        "-sv",
        f"--alluredir=allure-results/{test_suite}",
        "-m",
        test_suite,
    ]

    if num_threads > 1:
        command.extend(["-n", str(num_threads)])

    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ) as process:
        for line in process.stdout:
            print(f"[{test_suite}] {line}", end="")
        process.wait()

        if process.returncode != 0:
            print(f"[{test_suite}] завершился с кодом {process.returncode}")
        return process.returncode


def run_test_suite(params: tuple[str, int]) -> int:
    return run_tests(*params)


if __name__ == "__main__":
    # (маркер набора, число параллельных браузеров внутри набора)
    test_suites = [("smoke", 3), ("regress", 2)]

    with ProcessPoolExecutor(max_workers=len(test_suites)) as executor:
        results = list(executor.map(run_test_suite, test_suites))

    # Ненулевой код выхода, если упал хотя бы один набор — иначе CI будет зелёным при красных тестах
    sys.exit(max(results))
