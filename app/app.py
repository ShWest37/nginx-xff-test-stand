#!/usr/bin/env python3
# Импортируем классы для создания минимального HTTP-сервера из стандартной библиотеки
from http.server import HTTPServer, BaseHTTPRequestHandler
# Импортируем модуль для работы с JSON
import json

# Объявляем класс-обработчик HTTP-запросов
class XFFHandler(BaseHTTPRequestHandler):
    # Метод вызывается автоматически при получении GET-запроса
    def do_GET(self):
        # Извлекаем заголовок X-Forwarded-For, если нет — подставляем заглушку
        xff_value = self.headers.get('X-Forwarded-For', 'Header not present')
        
        # Формируем ответ в виде JSON-словаря
        response = {"X-Forwarded-For": xff_value}
        
        # Отправляем HTTP-статус 200 OK
        self.send_response(200)
        # Указываем тип контента: JSON в кодировке UTF-8
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        # Завершаем заголовки (отправляем CRLF)
        self.end_headers()
        # Сериализуем словарь в JSON, кодируем в байты и записываем в сокет ответа
        self.wfile.write(json.dumps(response, indent=2, ensure_ascii=False).encode('utf-8'))
    
    # Подавляем стандартное логирование запросов в stdout контейнера
    def log_message(self, format, *args):
        pass

# Точка входа: выполняется при прямом запуске скрипта
if __name__ == '__main__':
    # Создаём сервер, слушающий все интерфейсы контейнера на порту 8080
    server = HTTPServer(('0.0.0.0', 8080), XFFHandler)
    # Выводим сообщение в лог (видно в docker compose logs)
    print("✅ Backend listening on :8080")
    # Запускаем бесконечный цикл обработки запросов
    server.serve_forever()
