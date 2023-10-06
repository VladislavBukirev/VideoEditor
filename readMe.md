Python Task: Медиа редактор
# Видео редактор
Автор проекта: Гуриков Максим, Букирев Владислав, фт - 103 - 2

## Описание
Данное приложение является реализацией простого видео редактора и может быть использовано
как по прямому назначению, так и в качестве reference solution.

## Требования
* Python версии не ниже 3.10
* moviePy версии не ниже 1.0.3
* PyQt5 версии не ниже 5.15.9
* K-Lite codec для работы встроенного проигрывателя

## Фичи
* Ускорение/Замедление видео
* Поворот видео
* Кроп
* Вставка картинки
* Вырезание фрагмента видео
* Работа с фрагментами
* Объединения двух видео
* Сохраниения произведенных действий в шаблон

## Состав проекта
* requirements.txt
* VideoEditor.py - собственно сам редактор, в файле собраны функции осуществляющие обработку пользовательского ввода 
* GUI.py - файл содержит класс окна видео редактора
* Tests - тесты
* temp_output.mp4 - файл содержащий промежуточный результат работы программы и из которого проигрывается видео
* templates.txt - файл с сохраннеными шаблонами

## Управление - Шорткаты
* Ctrl-O, Ctrl-S, Shift-Ctrl-S - открыть, сохранить, сохранить как
* Ctrl-Z, Ctrl-R - undo/redo

