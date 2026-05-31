Nginx X-Forwarded-For Chain Test Stand
Тестовое задание для позиции DevOps-инженер: демонстрация безопасной передачи заголовка X-Forwarded-For через цепочку обратных прокси с защитой от подделки (spoofing).
 
Где скачать и запустить стенд
🔗 Репозиторий с решением

https://github.com/ShWest37/nginx-xff-test-stand

 Быстрый старт

# 1. Клонируйте репозиторий
git clone https://github.com/ShWest37/nginx-xff-test-stand
cd nginx-xff-test-stand

# 2. Запустите стенд (требуется Docker Engine 20.10+ и Compose v2)
docker compose up -d --build

# 3. Дождитесь запуска и проверьте статус
docker compose ps
# ✅ Все 4 сервиса должны быть в статусе "Up"
# 4. Выполните протокол тестирования:

Тест 1: Прямой запрос (1 hop)
curl.exe -s http://localhost:8081
 Ожидаемый вывод:
{
  "X-Forwarded-For": "192.168.100.1"
}

Тест 2: Цепочка 2 nginx

curl.exe -s http://localhost:8082

 Ожидаемый вывод:
{
  "X-Forwarded-For": "192.168.100.1, 192.168.100.x"
}

(Цепочка из клиента + одного внутреннего прокси)

Тест 3: Полная цепочка 3 nginx

curl.exe -s http://localhost:8083

{
  "X-Forwarded-For": "192.168.100.1, 192.168.100.y, 192.168.100.z"
}

(Клиент + два внутренних прокси)

 Тест 4: Защита от spoofing (КЛЮЧЕВОЙ!)

curl.exe -s -H "X-Forwarded-For: 99.99.99.99, 88.88.88.88" http://localhost:8083

Ожидаемый вывод:

{
  "X-Forwarded-For": "192.168.100.1, 192.168.100.y, 192.168.100.z"
}
# 5. Проверка статусов контейнеров:

docker compose ps

NAME                          IMAGE           STATUS          PORTS
nginx-xff-test-stand-app-1    python:3.11-alpine   Up (healthy)   8080/tcp
nginx-xff-test-stand-nginx1-1 nginx:alpine         Up             0.0.0.0:8081->80/tcp
nginx-xff-test-stand-nginx2-1 nginx:alpine         Up             0.0.0.0:8082->80/tcp
nginx-xff-test-stand-nginx3-1 nginx:alpine         Up             0.0.0.0:8083->80/tcp

 Структура проекта

.
├── docker-compose.yml          # Оркестрация: 4 сервиса + фиксированная сеть 192.168.100.0/24
├── app/
│   ├── app.py                  # Zero-dependency HTTP-сервер на стандартной библиотеке Python
│   └── Dockerfile              # Сборка образа на python:3.11-alpine (~50 МБ)
├── nginx/
│   ├── nginx.conf              # Базовый конфиг (без map — логика в отдельных файлах)
│   ├── nginx1.conf             # INTERNAL: proxy_pass → app, расширяет цепочку
│   ├── nginx2.conf             # INTERNAL: proxy_pass → nginx1, расширяет цепочку
│   └── nginx3.conf             # EDGE: proxy_pass → nginx2, перезаписывает заголовок
├── README.md                   # Этот файл
└── .gitignore                  # Исключения для Git

Требования к окружению:

Компонент
Минимальная версия
Проверка
Docker Engine
20.10+
docker --version
Docker Compose
v2.0+
docker compose version
curl
любой
curl --version
ОС
Linux / macOS / WSL2 на Windows
—
💡 Установка Docker: https://docs.docker.com/engine/install/



### Архитектура безопасности

Решение реализует паттерн Trusted Proxy Boundary:

| Прокси | Роль | Обработка `X-Forwarded-For` |
|--------|------|----------------------------|
| `nginx3` (порт 8083) | **EDGE** (входная точка) | Перезаписывает заголовок: `$remote_addr` — игнорирует входящие значения |
| `nginx2` (порт 8082) | **INTERNAL** | Расширяет цепочку: `$proxy_add_x_forwarded_for` |
| `nginx1` (порт 8081) | **INTERNAL** | Расширяет цепочку: `$proxy_add_x_forwarded_for` |

Это соответствует реальной архитектуре, где только граничный прокси (Cloudflare, AWS ALB, первый nginx) доверяется для определения реального IP клиента.

### 🧪 Тест на защиту от spoofing

```bash
# Подделываем заголовок
curl -H "X-Forwarded-For: 99.99.99.99" http://localhost:8083

# Ожидаемый результат: подставленные значения отсутствуют
{"X-Forwarded-For": "192.168.100.1, 192.168.100.x, 192.168.100.y"}

 Затраченное время

Проектирование архитектуры и логики безопасности
~1 ч
Написание конфигураций nginx, Dockerfile, docker-compose
~1.5 ч
Отладка цепочек и защита от spoofing
~1 ч
Документирование, тест-протокол, подготовка к отправке
~1.5 ч
Итого чистое время
~5 часов

Контакты автора:

Имя
[Александр Чалов]
Позиция
DevOps-инженер / Системный администратор
Email
[aleksandr_7@bk.ru]
Telegram
[@AleksITDev]
GitHub
https://github.com/ShWest37/nginx-xff-test-stand

💡 Примечание для проверяющего:
Если вы хотите протестировать стенд на своём VPS с публичным доступом, достаточно:
Открыть порты 8081–8083 в фаерволе провайдера
Заменить localhost на публичный IP в командах curl
В продакшене первым элементом цепочки будет реальный внешний IP клиента, а не 192.168.100.1

Документ актуален на момент отправки: 31 мая 2026
Решение протестировано на: WSL2 (Debian), Docker Engine 24.0, Docker Compose v2.20
