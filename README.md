# SberMenu
![alt text](./static/svg/SberMenuLogo.svg)
## Запуск проекта в dev-режиме
### Установите и активируйте виртуальное окружение
 ```bash
python -m venv venv
source venv/bin/activate
```
В Windows комманда активации будет отличаться:
```bat
venv\Scripts\activate
```

### Установите зависимости
* Для разработки установите зависимости из файла requirements/dev.txt
    ```shell
    pip install -r requirements/dev.txt
    pip install Werkzeug==2.3.0
    ```

* Для тестирования установите зависимости из файла requirements/test.txt
    ```shell
    pip install -r requirements/test.txt
    ```
* Для прода установите зависимости из файла requirements/prod.txt
    ```shell
    pip install -r requirements/prod.txt
    pip install Werkzeug==2.3.0
    ```

### Выполните команду:
```
python server.py
```
или
```
python3 server.py
```

### Диаграма DB
![DataBase](dtbase.jpg)

# Комманда - ChinaGriB
