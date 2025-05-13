from vnstat_parser import parse_5min, parse_hourly, parse_hourly_full, parse_daily, parse_daily_full, parse_monthly, parse_monthly_full
from flask import Flask, render_template, request
from collections import defaultdict
import logging
import calendar
from config import *  # Импортируем все настройки из config.py

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

# Константы для иконок
ICON_CLOSED = '►'  # Закрытая иконка (треугольник вправо)
ICON_OPENED = '▼'  # Открытая иконка (треугольник вниз)

def build_nested_stats():
    # Собираем вложенную структуру: год -> месяц -> день -> час -> 5мин
    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
    
    # Получаем все данные
    min5_data = parse_5min()
    hourly_data = parse_hourly()
    daily_data = parse_daily()
    monthly_data = parse_monthly()
    
    logging.info(f"[build_nested_stats] Got data: {len(min5_data)} 5min, {len(hourly_data)} hourly, {len(daily_data)} daily, {len(monthly_data)} monthly")
    
    # Заполняем месячные данные
    for row in monthly_data:
        if not row.get('date'): continue
        y, m = row['date'].split('-')
        tree[y][m]['_month'] = row
        logging.info(f"[build_nested_stats] Added month data: {y}-{m}")
    
    # Заполняем дневные данные
    for row in daily_data:
        if not row.get('date'): continue
        y, m, d = row['date'].split('-')
        tree[y][m][d]['_day'] = row
        logging.info(f"[build_nested_stats] Added day data: {y}-{m}-{d}")
    
    # Заполняем часовые данные
    for row in hourly_data:
        if not row.get('date'): continue
        y, m, d = row['date'].split('-')
        h = row['hour']
        tree[y][m][d][h]['_hour'] = row
        logging.info(f"[build_nested_stats] Added hour data: {y}-{m}-{d} {h}:00")
    
    # Заполняем 5-минутные данные
    for row in min5_data:
        if not row.get('date'): continue
        y, m, d = row['date'].split('-')
        h = row['hour']
        tree[y][m][d][h][row['minute']] = row
        logging.info(f"[build_nested_stats] Added 5min data: {y}-{m}-{d} {h}:{row['minute']}")
    
    return tree

@app.route('/')
def dashboard():
    years = int(request.args.get('years', 1))
    stats_tree = build_nested_stats()
    
    # Считаем реальное количество лет с данными
    available_years = sorted(stats_tree.keys(), reverse=True)
    actual_years = len(available_years)
    
    # Ограничиваем years тем что реально есть
    years = min(years, actual_years)
    
    # Оставляем только запрошенное количество лет
    filtered_tree = {}
    for year in available_years[:years]:
        filtered_tree[year] = stats_tree[year]
    
    return render_template(
        'dashboard.html',
        min5=parse_5min(),
        stats_tree=filtered_tree,
        years=years,
        has_more_years=years < actual_years,
        month_names=MONTH_NAMES,
        ICON_CLOSED=ICON_CLOSED,
        ICON_OPENED=ICON_OPENED,
        interface=VNSTAT_IFACE
    )

if __name__ == '__main__':
    logging.basicConfig(
        filename=LOG_FILE,
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )
    app.run(debug=DEBUG, host=WEB_HOST, port=WEB_PORT) 