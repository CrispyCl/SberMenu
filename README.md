<div id="header" align="center">
    <div>
        <img src="https://media4.giphy.com/media/gjrYDwbjnK8x36xZIO/giphy.gif?cid=ecf05e476ht8f5g4s8rz6uaiu8lfpmhkz0u3wgd4dro098xo&ep=v1_gifs_related&rid=giphy.gif&ct=s" width="100">
        <h1>
            <b>SberMenu</b>
        </h1>
    </div>
</div>


<div align="center">
  <img src="https://media.giphy.com/media/dWesBcTLavkZuG35MI/giphy.gif" width="500" height="300"/>
</div>

<div align="center">
    <h1>
        <b> Комманда - ChinaGriB </b>
    </h1>

### 🛠️ Используемые языки и инструменты :


<div>
    <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/html5/html5-original-wordmark.svg" width="80" height="80">&nbsp;
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" width="80" height="80">&nbsp;
    <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/javascript/javascript-original.svg" width="80" height="80">&nbsp;
    <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/python/python-original-wordmark.svg" width="80" height="80">&nbsp;
    <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/flask/flask-original-wordmark.svg" width="80" height="80">&nbsp;
    <!-- <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/sqlite/sqlite-original-wordmark.svg" width="80" height="80">&nbsp; -->
    <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/sqlalchemy/sqlalchemy-original-wordmark.svg" width="80" height="80">&nbsp;
    <!-- <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/tailwindcss/tailwindcss-original-wordmark.svg" width="80" height="80">&nbsp; -->
    <!-- <img src="https://raw.githubusercontent.com/devicons/devicon/55609aa5bd817ff167afce0d965585c92040787a/icons/react/react-original-wordmark.svg" width="80" height="80">&nbsp; -->
</div>

</div>





## Запуск проекта в dev-режиме
### Установите виртуальное окружение
 ```bash
python -m venv venv
```
### Активируйте виртуальное окружение
```bash
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
