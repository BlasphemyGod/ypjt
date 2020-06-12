# Telegram-бот "Тренер"
### Проблема и решение
Каждый из нас должен держать себя в форме. 
Но не каждый способен грамотно распределить своё время
для регулярных тренировок. Решение – наш бот! 
Он поможет вам заниматься максимально эффективно. 
Сам тренер является одноимённым персонажем 
фильма Гая Ричи "Джентельмены".
### Удобное использование
Бот ориентирован на взаимодействие с пользователем
и, мы постарались сделать всё, чтобы пользователю
было комфортно: кастомные клавиатуры для быстрого и удобного
взаимодействия с ботом, определение часового пояса по
геолокации, оплата абонемента через телеграм.
### Персонаж Тренера
Мы пытались создать эмоциональную привязку к Тренеру
для того, чтобы пользователю было совестно прогуливать
тренировки, и укорительный взгляд Колина Фаррелла нам в этом помогает.
Наши собственные стикеры выражают его эмоции, а
слабоватый, на данный момент, ИИ использует фразы, сказанные тренером
в фильме, ведь это очень харизматичный и запоминающийся персонаж.
### Принцип работы с ботом
При запуске бота пользователю предлагается заполнить 
свои 'максимумы' – лучшие результаты в упражнениях, 
на основе которых будет составлена индивидуальная 
программа упражнений, по которым пользователь будет заниматься. 
После чего "Тренер" будет в удобное вам время проводить тренировки. 
Есть возможность приобрести абонемент, 
который позволяет записываться на несколько тренировок в день. 
### Как использовать
Для использования бота нужно:\
•Найти его в телеграме @Coach_the_Gentlebot\
•Нажать "start"\
•Дальнейшие инструкции вам даст сам Тренер, так как бот 
ориентирован на взаимодействие с пользователем и интуитивно понятен.
## Принцип работы бота
### Сбор и хранение данных
После нажатия кнопки "старт" бот задаёт 
вопросы и собирает информацию о пользователе.\
Сначала он спрашивает как обращаться к пользователю, 
затем определяет часовой пояс по геолокации, 
но на всякий случай переспрашивает у юзера 
правильно ли он его определил, после он спрашивает об упражниниях 
которые юзер хотел бы делать и, в заключение спрашивает 
когда пользавателю удобно заниматься.

Всё это он записывает в базу данных, 
а время тренировок(с учётом часового пояса) ещё и в json файл 
для последующей рассылки уведомлений о тренировках.
Все введённые данные можно изменить в главном меню бота.

Так же в главном меню можно побеседовать с ИИ(все мы знаем 
что использование ИИ, даже там где не надо, увеличивает цену 
конечного продукта).
### Тренировка и абонемент
Каждые 5 минут бот проверяет json файл. 
Ключами являются день недели и текущее время, а в качестве 
значения выступает id пользователя которому нужно 
отправить напоминание о тренировке.

Сама тренировка является интерактивной и если, допустим, 
пользователю было тяжело выполнить упражниния, то Тренер 
уменьшит нагрузку и наоборот. 

При покупке платного абонемента(для теста даётся номер карты, 
чтобы продемонстрировать работоспособность этой функции) юзер
получает дополнительные функции, например, возможность добавлять
несколько тренировок в день для большей продуктивности.
Так же абонемент даёт возможность получать от Тренера челенджи,
которые представляют собой разнообразные спортивные задания.
### Защита от дураков и Дурова
Бот защищён от непредусмотренного поведения пользователя.
Если пользователь случайно, или специально, ввёл некорректные
данные, то Тренер переспросит или усмехнётся над тщетными попытками
себя положить. Так же присутсвует защита от падения серверов 
телеграма, а они довольно часто падают или уходят на ремонт.
## Дальнейшее развитие
Мы работаем над соревновательной системой которая позволит
следить за прогрессом друзей и не отставать от них. Дух 
соревновательности будет побуждать людей ставить рекорды и
выполнять челенджи, а также не даст заскучать.
## Какие технологии были использованы
Пишу на всякий случай что присутствует в боте\
•Работа с API телеграма\
•Работа с платежами через телеграм\
•Работа с  ООП\
•Работа с json файлами\
•Работа с базами данных\
•Мультипроцессы\
•Работа с геолокацией\
•Работа с часовыми поясами\
•Искусственный интеллект\
•Логирование\
•Собственные стикеры\
Бот запущен на pythonanywhere
## Как запустить
Для запуска бота необходимо:\
•Установить все сторонние библиотеки (requirements.txt)\
•Получить 3 токена (где их искать написанно в config.py)\
•Убедиться что файлы config.py, data.db, messages.py, training.json, main.py присутсвуют в папке с проектом\
•Запустить main.py через vpn.