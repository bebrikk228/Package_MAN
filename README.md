# APK Dependency Graph Visualizer (Вариант №27)

## 1. Общее описание
CLI-инструмент для анализа и визуализации графа зависимостей пакетов формата
Alpine Linux (`apk`) без использования сторонних менеджеров пакетов и библиотек
получения зависимостей.

На текущем этапе (Этап 2) реализована загрузка и разбор индекса репозитория
`APKINDEX.tar.gz` средствами стандартной библиотеки Python, поиск заданной
версии пакета и вывод всех его прямых зависимостей.

## 2. Описание всех функций и настроек
Приложение принимает следующие опции командной строки:
- `-p`, `--package` (обязательный): имя анализируемого пакета (например, `curl`).
- `-r`, `--repo` (обязательный): URL-адрес репозитория `apk` или путь к файлу
  тестового репозитория.
- `-t`, `--test-mode` (флаг): включение режима работы с локальным файлом.
- `-v`, `--version` (обязательный): точная версия анализируемого пакета.
- `-o`, `--output` (необязательный, по умолчанию `graph.png`): имя выходного
  PNG-файла для изображения графа.

Основные модули в `src/`:
- `validator.py`: функции валидации параметров (`validate_package_name`,
  `validate_version`, `validate_repository`, `validate_output_file`) и
  исключение `ConfigValidationError`.
- `cli.py`: модель `AppConfig`, функции `build_parser` и `parse_config`.
- `apk_parser.py`: загрузка и распаковка `APKINDEX.tar.gz` (`fetch_apkindex_text`,
  `extract_index_from_bytes`, `download_bytes`), парсинг записей
  (`build_index_data`, `parse_record_block`, `parse_depends_entry`,
  `parse_provides_entry`, `strip_version_constraint`) и разрешение прямых
  зависимостей (`resolve_direct_dependencies`).
- `main.py`: точка входа (`run`, `load_index_text`, `format_dependencies`).

## 3. Описание команд для сборки проекта и запуска тестов
Проект использует только стандартную библиотеку Python 3 и не требует
установки сторонних зависимостей.

Запуск модульных тестов:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## 4. Примеры использования
Получение прямых зависимостей реального пакета из официального зеркала Alpine Linux:
```bash
./run.sh -p busybox -r [https://dl-cdn.alpinelinux.org/alpine/v3.20/main](https://dl-cdn.alpinelinux.org/alpine/v3.20/main) -v 1.36.1-r31
```

Пример обработки ошибки (несуществующая версия пакета):
```bash
./run.sh -p busybox -r [https://dl-cdn.alpinelinux.org/alpine/v3.20/main](https://dl-cdn.alpinelinux.org/alpine/v3.20/main) -v 0.0.1-r0
```
