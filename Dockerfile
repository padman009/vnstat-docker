FROM ubuntu:22.04

# Устанавливаем vnstat и Python
RUN apt-get update && apt-get install -y vnstat python3 python3-pip

# Устанавливаем зависимости 
COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt

# Копируем приложение
COPY *.py /app/
COPY templates /app/templates/

# Настройка vnstat
RUN mkdir -p /var/lib/vnstat
ENV INTERFACE="eth0"

# Порт для веб-интерфейса
EXPOSE 5000

# Запускаем vnstat и приложение
CMD service vnstat start && python3 dashboard.py 