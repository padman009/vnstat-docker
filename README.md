# vnStat Dashboard

Веб-интерфейс для мониторинга сетевого трафика на базе vnstat.

![Скриншот](https://i.imgur.com/example.png)

## Возможности

- Отображение статистики трафика по годам, месяцам, дням, часам и 5-минуткам
- Древовидная структура с раскрывающимися элементами
- Настраиваемый интерфейс
- Динамическое обновление данных

## Требования

- Python 3.6+
- vnStat
- Flask

## Установка

### 1. Установка vnstat (если еще не установлен)

```bash
sudo apt update
sudo apt install vnstat
```

### 2. Клонирование репозитория

```bash
git clone https://github.com/yourusername/vnstat-docker.git
cd vnstat-docker
```

### 3. Установка зависимостей Python

```bash
pip install -r requirements.txt
```

### 4. Настройка

Отредактируйте файл `config.py` для настройки сетевого интерфейса и других параметров:

```python
# Сетевой интерфейс для мониторинга
VNSTAT_IFACE = "eth0"  # Измените на свой интерфейс
```

### 5. Запуск

```bash
python dashboard.py
```

После запуска откройте в браузере http://localhost:5000

## Запуск через Docker(опционально)

```bash
# Сборка образа
docker build -t vnstat-dashboard .

# Запуск контейнера
docker run -d -p 5000:5000 --net=host -v $(pwd)/config.py:/app/config.py --name vnstat-dashboard vnstat-dashboard
```

## Структура проекта

- `dashboard.py` - Основное Flask-приложение
- `vnstat_parser.py` - Парсер вывода команды vnstat
- `config.py` - Файл конфигурации
- `templates/` - HTML-шаблоны
- `requirements.txt` - Зависимости Python

## Лицензия

MIT 