# Парсинг PEP

### Функции
- "what's new" - вывод всех статей с изменениями в очередной версии Python
- "latest-versions" - вывод ссылок на документацию разных версий Python
- "download" - загрузка последней версии документации в формате pdf
- "pep" - подсчет количества PEP в разных статусах

### Установка проекта    
Клонируйте репозиторий:
```
git clone git@github.com:sldmxm/bs4_parser_pep.git
```
Разверните виртуальное окружение и установите зависимости
```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Аргументы командной строки
Обязательный аргумент - режим работы
```
python main.py (whats-new|latest-versions|download,pep)
```
Опциональные аргументы:
```
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```

### Технологии в проекте
- Python v.3.7+
- Beautiful Soup
- tqdm
- requests_cache
- PrettyTable