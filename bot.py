import logging
import re

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import paramiko
import os
from pathlib import Path
from dotenv import load_dotenv

import psycopg2
from psycopg2 import Error

# Подключает логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

logger = logging.getLogger(__name__)

#Чтения переменных окружения из файла .env
load_dotenv(dotenv_path='.env')
bot_token = os.getenv('TOKEN')
chat_id = os.getenv('BOT')
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
username_db = os.getenv('DB_USER')
password_db = os.getenv('DB_PASSWORD')
port_db = os.getenv('DB_PORT')
host_db = os.getenv('DB_HOST')
database = os.getenv('DB_DATABASE')

#Подсоединение к базе данных на Linux машине:
def db_connect(command_db, name_command_db, host=host_db, username=username_db, password=password_db, port=port_db, database=database):
    connection = None

    try:
        connection = psycopg2.connect(user=username, password=password, host=host, port=port, database=database)
        cursor = connection.cursor()
        if name_command_db == "findPhoneNumbers":
            for phoneNambers in command_db:
                cursor.executemany(
                    '''
                    INSERT INTO phone_numbers (phone_number) VALUES (%s);
                    ''', [(phoneNambers,)])
                connection.commit()
                logging.info("Команда успешно выполнена. В таблицу phone_numbers добавлен новый номер!")
                logger.info(str(phoneNambers))
        elif name_command_db == "findEmail":
            for emails in command_db:
                cursor.executemany(
                    '''
                    INSERT INTO email (email) VALUES (%s);
                    ''', [(emails,)])
                connection.commit()
                logging.info("Команда успешно выполнена. В таблицу email добавлен новый email!")
                logger.info(str(emails))
        elif name_command_db == "getPhoneNumbers":
            cursor.execute(
                '''
                SELECT * FROM phone_numbers;
                ''')
            data_s = cursor.fetchall()
            logging.info("Команда успешно выполнена. Выведены данные о номерах телефонов из phone_numbers!")
        elif name_command_db == "getEmails":
            cursor.execute(
                '''
                SELECT * FROM email;
                ''')
            data_s = cursor.fetchall()
            logging.info("Команда успешно выполнена. Выведены данные о номерах телефонов из email!")

    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        if (name_command_db == "getPhoneNumbers") or (name_command_db == "getEmails"):
            logger.info(str(data_s))
            return str(data_s)  # Возвращает содержимое data_s

#1.а. Поиск номеров телефонов:
def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получает текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}')  # формат номера телефона

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищет номера телефонов

    logger.info(f"{phoneNumberList}")

    if not phoneNumberList:  # Обрабатывает случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершает выполнение функции

    db_connect(phoneNumberList, 'findPhoneNumbers')  # Записываем номера телефонов в базу данных

    phoneNumbers = ''  # Создаёт строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    if len(phoneNumberList) == 1:  # Сообщаем пользователю об успешной записи номеров в базу данных
        update.message.reply_text(f'Номер телефона успешно добавлен в базу данных: \n{phoneNumbers}')
    else:
        update.message.reply_text(f'Номера телефонов успешно добавлены в базу данных: \n{phoneNumbers}')
    phoneNumbers = ''  # Очищаю phoneNumbers от старых данных
    return ConversationHandler.END  # Завершает работу обработчика диалога

#1.b. Поиск email-адресов:
def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email-адресов: ')
    return 'findEmail'


def findEmail(update: Update, context):
    user_input = update.message.text  # Получает текст, содержащий(или нет) email-адреса

    emailRegex = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')  # формат email-адресов

    emailList = emailRegex.findall(user_input)  # Ищет email-адреса

    logger.info(f"{emailList}")

    if not emailList:  # Обрабатывает случай, когда email-адресов нет
        update.message.reply_text('Email-адреса не найдены.')
        return  # Завершает выполнение функции

    db_connect(emailList, 'findEmail')  # Записывает email-ы в базу данных

    emails = ''  # Создаёт строку, в которую будем записывать email-адреса
    for i in range(len(emailList)):
        emails += f'{i + 1}. {emailList[i]}\n'  # Записываем очередной email-адрес

    if len(emailList) == 1:  # Сообщаем пользователю об успешной записи email в базу данных
        update.message.reply_text(f'Email успешно добавлен в базу данных: \n{emails}')
    else:
        update.message.reply_text(f'Электронные почты успешно добавлены в базу данных: \n{emails}')
    emails = ''  # Очищаю emails от старых данных
    return ConversationHandler.END  # Завершает работу обработчика диалога

#2. Проверка сложности пароля регулярным выражением.
def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')
    return 'verifyPassword'

def verifyPassword (update: Update, context):
    user_input = update.message.text  # Получает текст, содержащий(или нет) пароль

    #Требования к паролю:
    #Пароль должен содержать не менее восьми символов.
    #Пароль должен включать как минимум одну заглавную букву (A–Z).
    #Пароль должен включать хотя бы одну строчную букву (a–z).
    #Пароль должен включать хотя бы одну цифру (0–9).
    #Пароль должен включать хотя бы один специальный символ, такой как !@#$%^&*().

    passwordRegex = re.compile(r'(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}')  # формат пароля

    password = passwordRegex.search(user_input)  # Ищет пароль подходящий под формат

    logger.info(f"{password}")

    if not password:  # Обрабатывает случай, когда пароля не подходит под формат
        update.message.reply_text('Пароль простой.')  # Отправляет сообщение пользователю
        return ConversationHandler.END  # Завершает выполнение функции
    else:
        update.message.reply_text('Пароль сложный.')  # Отправляет сообщение пользователю
        return ConversationHandler.END  # Завершает выполнение функции


#Подсоединение по ssh c Linux машиной:
def ssh_connect(command, host=host, username=username, password=password, port=port):
    client = paramiko.SSHClient()  # Создается экземпляр класса SSHClient из библиотеки Paramiko.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Устанавливается политика добавления хост-ключей автоматически, чтобы избежать ошибок вроде paramiko.ssh_exception.SSHException: Server 'hostname' not found in known_hosts.
    client.connect(hostname=host, username=username, password=password, port=port)  # Устанавливается соединение с удаленным сервером, используя заданные параметры.

    stdin, stdout, stderr = client.exec_command(command=command)  # Выполняется команда command на удаленном сервере через SSH. Полученные данные записываются в переменные stdin, stdout и stderr.
    data = stdout.read() + stderr.read()  # Содержимое stdout и stderr объединяется в переменной data.
    client.close()  # Соединение с сервером закрывается.

    logger.info(str(data))

    return str(data)  # Возвращает содержимое data


#3. Мониторинг Linux-системы
#3.1 Сбор информации о системе:
    #3.1.1 О релизе.
def getRelease(update: Update, context):
    answer = ssh_connect(command="uname -r")  # Создается переменная answer, в которой сохраняется результат выполнения функции ssh_connect с аргументом command="uname -r".
    answer = answer.replace('b\'', "").replace("\\n\'", "")  #В строке answer происходит замена подстрок 'b\'' на пустую строку и подстроки "\\n\'" на пустую строку.

    update.message.reply_text(answer)  # Отправляет сообщение пользователю
    return ConversationHandler.END  # Завершает выполнение функции

    #3.1.2 Об архитектуры процессора, имени хоста системы и версии ядра.
def getUname(update: Update, context):
    answer = ssh_connect(command="uname -m && hostname && uname -r")
    answer = answer.replace('b\'', "").replace("\\n\'", "").replace("\\n", " ")

    update.message.reply_text(answer)
    return ConversationHandler.END

    #3.1.3 О времени работы.
def getUptime(update: Update, context):
    answer = ssh_connect(command="uptime")
    answer = answer.replace('b\'', "").replace("\\n\'", "")

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.2 Сбор информации о состоянии файловой системы.
def getDf(update: Update, context):
    answer = ssh_connect(command="df -h")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.3 Сбор информации о состоянии оперативной памяти.
def getFree(update: Update, context):
    answer = ssh_connect(command="free")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.4 Сбор информации о производительности системы.
def getMpstat(update: Update, context):
    answer = ssh_connect(command="mpstat")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.5 Сбор информации о работающих в данной системе пользователях.
def getW(update: Update, context):
    answer = ssh_connect(command="w")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.6 Сбор логов
    #3.6.1 Последние 10 входов в систему.
def getAuths(update: Update, context):
    answer = ssh_connect(command="last")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END

    #3.6.2 Последние 5 критических события.
def getCritical(update: Update, context):
    answer = ssh_connect(command="journalctl -p crit -n 5")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.7 Сбор информации о запущенных процессах.
def getPs(update: Update, context):
    answer = ssh_connect(command="ps -u")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.8 Сбор информации об используемых портах.
def getSs(update: Update, context):
    answer = ssh_connect(command="ss | head -n 15")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END


#3.9 Сбор информации об установленных пакетах.
def getAptListCommand(update: Update, context):
    update.message.reply_text('Введите название пакета:\nДля просмотра всех пакетов введите all: ')
    return 'getAptList'

def getAptList(update: Update, context):
    user_input = update.message.text  # Получает текст, содержащий либо название пакета, либо all

    if user_input == "all":
        answer = ssh_connect(command="apt list --installed | head -n 15")  # Если пользователь ввёл all, то выводит command="apt list --installed" для вывода всех пакетов
    else:
        answer = ssh_connect(command="apt list --installed " + user_input)  # Ecли пользователь ввёл название пакета, то выводит  command="apt list --installed " + user_input для вывода определённого пакета

    answer = answer.encode().decode('unicode-escape').encode('latin1').decode('utf-8').replace("b'", "").replace("'", "")
    if 'WARNING: apt does not have a stable CLI interface.' in answer:  #Условие, которое будет игнорировать вывод, содержащий предупреждение
        answer = answer.replace('WARNING: apt does not have a stable CLI interface. Use with caution in scripts.', '')

    update.message.reply_text(answer)  # Отправляет сообщение пользователю
    return ConversationHandler.END  # Завершает работу обработчика диалога


#3.10 Сбор информации о запущенных сервисах.
def getServices(update: Update, context):
    answer = ssh_connect(command="systemctl list-units --type service | head -n 15")
    answer = answer.replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(answer)
    return ConversationHandler.END

#Практика 2. 4. Настроить вывод логов о репликации из /var/log/postgresql/ в тг-бот
def getReplLogs(update: Update, context):
    answer = ssh_connect(command="tail -n 10 /var/log/postgresql/postgresql-12-main.log")
    answer = answer.encode().decode('unicode-escape').encode('latin1').decode('utf-8').replace("b'", "").replace("'",
                                                                                                                 "")
    if 'WARNING: apt does not have a stable CLI interface.' in answer:  # Условие, которое будет игнорировать вывод, содержащий предупреждение
        answer = answer.replace('WARNING: apt does not have a stable CLI interface. Use with caution in scripts.', '')

    update.message.reply_text(answer)  # Отправляет сообщение пользователю
    return ConversationHandler.END  # Завершает работу обработчика диалога

#5. Реализовать возможность вывод данных из таблиц через бота.
def getEmails(update: Update, context):
    answer = db_connect(None, 'getEmails')  # Запрос данных из таблицы email
    answer = (answer.replace("[", '').replace("]", "").replace("'", "")
              .replace("(","").replace("),",")~").replace(")","")
              .replace(",", ")").replace("~",""))
    update.message.reply_text(f'Email записанные в базу данных: \n{answer}')  # Отправляет сообщение пользователю
    return ConversationHandler.END  # Завершает работу обработчика диалога


def getPhoneNumbers(update: Update, context):
    answer = db_connect(None, 'getPhoneNumbers')  # Запрос данных из таблицы email
    answer = (answer.replace("[", '').replace("]", "").replace("'", "")
              .replace("(","").replace("),",")~").replace(")","")
              .replace(",", ")").replace("~",""))
    update.message.reply_text(f'Номера телефонов записанные в базу данных: \n{answer}')  # Отправляет сообщение пользователю
    return ConversationHandler.END  # Завершает работу обработчика диалога


def main():
    updater = Updater(bot_token, use_context=True)  # Создаёт программу обновлений и передаёт ей токен бота

    dp = updater.dispatcher  # Получает диспетчер для регистрации обработчиков

    # Обработчики диалога
    # Взаимодействия с этими командами происходит по следующему принципу:
    # 1. Пользователь выбирает команду
    # 2. Бот запрашивает текст
    # 3. Пользователь отправляет текст
    # 4. Бот вывод список найденных номеров телефона или email-адресов.

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
        },
        fallbacks=[]
    )

    #Взаимодействие с этой командой происходит по следующему принципу:
    #1. Пользователь выбирает команду
    #2. Бот запрашивает пароль
    #3. Пользователь отправляет пароль
    #4. Бот отвечает: ‘`Пароль простой`’ или ‘`Пароль сложный`’.

    convHandlerCheckPass = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    #Два варианта взаимодействия с этой командой:
    #1. Вывод всех пакетов;
    #2. Поиск информации о пакете, название которого будет запрошено у пользователя.

    convHandlerGetApt = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'getAptList': [MessageHandler(Filters.text & ~Filters.command, getAptList)],
        },
        fallbacks=[]
    )

    # Регистрирует обработчики команд
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerCheckPass)

    #Взаимодействия с этими командами происходит по следующему принципу:
    #1. Пользователь выбирает команду
    #2. Бот отправляет соответствующую информацию
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(convHandlerGetApt)
    dp.add_handler(CommandHandler("get_services", getServices))

    dp.add_handler(CommandHandler("get_repl_logs", getReplLogs))
    dp.add_handler(CommandHandler("get_emails", getEmails))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbers))

    # Запускает бота
    updater.start_polling()

    # Останавливает бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()