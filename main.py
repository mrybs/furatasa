try:
    import sys
    import random
    import sqlite3
    import datetime
    import threading
    import time
except ImportError as ie:
    print(f'Ошибка, какой-то из необходимых модулей не установился. Используйте python 3.10.\n{ie}')
    sys.exit(1)

try:
    from pyrogram import Client, filters, enums, types
except ImportError:
    print('Ошибка, необходимо установить модуль pyrogram')
    sys.exit(1)
try:
    import messages as msgs
except ImportError:
    print(f'В папку с этим исполняемым файлом нужно положить messages.py')
    sys.exit(1)
try:
    import cards
except ImportError:
    print(f'В папку с этим исполняемым файлом нужно положить cards.py')
    sys.exit(1)
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

config = configparser.ConfigParser()
config.read('config.ini')

bot = Client("my_account", api_id=config['pyrogram']['api_id'], api_hash=config['pyrogram']['api_hash'])

ava_enabled = False

@bot.on_message(filters.me)
async def echo(client, msg: types.Message):
    if msg.text is None: return

    config.read('config.ini')

    new_text = msg.text
    if config['inline']['enabled'] == 'true':
        cards_enum = [
            'VISA', 'MIR', 'MASTERCARD', 'MAESTRO', 'AMERICAN-EXPRESS', 'UNION-PAY'
        ]
        card = cards_enum[random.randint(0, len(cards_enum) - 1)]
        random_credit = f'{cards.gen(key=card)} ({cards.randomDate()[1]}/{cards.randomDate()[0]}, {cards.randomCCV()})'

        new_text = new_text.replace('%%chat id%%', str(msg.chat.id)) \
            .replace('%%random credit%%', random_credit) \
            .replace('%%my id%%', str(bot.me.id))
        if bot.me.username is not None:
            new_text = new_text.replace('%%my username%%', bot.me.username)
        if msg.chat.title is not None:
            new_text = new_text.replace('%%chat title%%', msg.chat.title)
        if msg.chat.username is not None:
            new_text = new_text.replace('%%chat username%%', msg.chat.username)

        result = db(f'select * from messages')
        if len(result) != 0:
            for _ in range(1, int(config['inline']['nesting'])):
                for i in result:
                    new_text = new_text.replace(f'%{i[0]}%', i[1])

    old_text = msg.text
    msg.text = new_text

    if msg.text == "!whoami":
        await bot.edit_message_text(msg.chat.id, msg.id, f'id: {bot.get_me().id}\nusername: @{bot.get_me().username}\nЗвать {bot.get_me().first_name}')
    elif msg.text == "!help":
        await bot.edit_message_text(msg.chat.id, msg.id, msgs.HELP)
    elif msg.text == "!chat":
        title = ""
        if msg.chat.title is not None:
            title = f'Название: {msg.chat.title}\n'
        link = ""
        if msg.chat.username is not None:
            link = f'Ссылка: https://t.me/{msg.chat.username}\n'
        bio = ""
        if msg.chat.bio is not None:
            bio = f'Био: {msg.chat.bio}\n'
        description = ""
        if msg.chat.description is not None:
            description = f'Описание: {msg.chat.description}\n'
        count = ""
        if msg.chat.members_count is not None:
            count = f'Количество участников: {msg.chat.members_count}\n'
        type = 'Это '
        if msg.chat.type == enums.ChatType.PRIVATE:
            type += 'приватный чат'
        elif msg.chat.type == enums.ChatType.BOT:
            type += 'чат с ботом'
        elif msg.chat.type == enums.ChatType.GROUP:
            type += 'групповой чат'
        elif msg.chat.type == enums.ChatType.SUPERGROUP:
            type += 'супергруппа'
        elif msg.chat.type == enums.ChatType.CHANNEL:
            type += 'канал'
        permissions = ''
        if msg.chat.permissions is not None:
            permissions = 'Обычному пользователю можно:\n'
            if msg.chat.permissions.can_send_messages:
                permissions += '    - Отправлять сообщения\n'
            if msg.chat.permissions.can_send_media_messages:
                permissions += '    - Отправлять медиафайлы\n'
            if msg.chat.permissions.can_send_other_messages:
                permissions += '    - Отправлять стикеры, анимации, игры и использовать inline-ботов\n'
            if msg.chat.permissions.can_send_polls:
                permissions += '    - Создавать опросы\n'
            if msg.chat.permissions.can_add_web_page_previews:
                permissions += '    - Добавлять превью к веб-страницам\n'
            if msg.chat.permissions.can_change_info:
                permissions += '    - Изменять информацию о группе\n'
            if msg.chat.permissions.can_invite_users:
                permissions += '    - Приглашать пользователей\n'
            if msg.chat.permissions.can_pin_messages:
                permissions += '    - Закреплять сообщения\n'
            if permissions == 'Обычному пользователю можно:\n':
                permissions = 'Обычному пользователю ничего нельзя\n'
        reactions = ''
        if msg.chat.available_reactions is not None:
            reactions = 'Доступные реакции: ' + ', '.join(msg.chat.available_reactions)
        await bot.edit_message_text(msg.chat.id, msg.id, f'id: {msg.chat.id}\n{title}{type}\n{link}{bio}{description}{reactions}{count}{"Чат верифицирован" if msg.chat.is_verified else "Чат не верифицирован"}\n{permissions}')
    elif msg.text.startswith('!dice'):
        number = 0
        try:
            number = int(msg.text[5:])
            await bot.edit_message_text(msg.chat.id, msg.id, str(random.randint(1, number)))
        except ValueError:
            await bot.delete_messages(msg.chat.id, [msg.id])
    if msg.text == '!random credit':
        rand = random.randint(0, 6)
        card = 'VISA'
        if rand == 0:
            card = 'MIR'
        elif rand == 1:
            card = 'VISA'
        elif rand == 2:
            card = 'MASTERCARD'
        elif rand == 3:
            card = 'MAESTRO'
        elif rand == 4:
            card = 'AMERICAN-EXPRESS'
        elif rand == 5:
            card = 'UNION-PAY'
        await bot.edit_message_text(msg.chat.id, msg.id, f'{cards.gen(key=card)} ({cards.randomDate()[1]}/{cards.randomDate()[0]}, {cards.randomCCV()})')
    elif msg.text.startswith('!msg read '):
        name = msg.text[10:]
        if msg.reply_to_message is not None:
            if msg.reply_to_message.text is not None:
                text = msg.reply_to_message.text
                db(f'insert into messages(name, text) values(\'{name}\', \'{text}\')')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!msg write '):
        name = msg.text[11:]
        result = db(f'select text from messages where name = \'{name}\'')
        if len(result) != 0: await bot.edit_message_text(msg.chat.id, msg.id, result[0][0])
        else: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!msg remove '):
        name = msg.text[12:]
        result = db(f'delete from messages where name = \'{name}\'')
        result = db(f'select text from messages where name = \'{name}\'')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!msg info':
        if msg.reply_to_message is not None:
            username = ''
            if msg.reply_to_message.from_user.username is not None:
                username = f'Username отправителя: @{msg.reply_to_message.from_user.username}\n'
            await bot.edit_message_text(msg.chat.id, msg.id, f'id: {msg.reply_to_message.id}\nid отправителя: {msg.reply_to_message.from_user.id}\n{username}Время: {msg.date.strftime("%Y.%m.%d %H:%m:%s")}\nДля большей информации о пользователе вызовите !user info')
        else: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!user info '):
        try:
            id = int(msg.text[11:])
            user = (await bot.get_users([id]))[0]
            contact = ('У вас в контактах' if user.is_contact else 'Не состоит у вас в контактах') + '\n'
            mutualContact = ('У вас есть общие знакомые' if user.is_mutual_contact else 'У вас нет общих знакомых') + '\n'
            deleted = 'Пользователь удален\n' if user.is_deleted else ''
            verify = ('Пользователь верифицирован' if user.is_verified else 'Пользователь не верифицирован') + '\n'
            premium = ('Пользователь является премиум аккаунтом' if user.is_premium else 'Пользователь не является премиум аккаунтом') + '\n'
            await bot.edit_message_text(msg.chat.id, msg.id, f'id: {user.id}\nusername: {user.username}\nИмя: {user.first_name}\n{contact}{mutualContact}{deleted}{verify}{premium}')
        except Exception: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!msg all':
        result = db(f'select name from messages')
        if len(result) != 0:
            all = []
            for i in result:
                all.append(i[0])
            await bot.edit_message_text(msg.chat.id, msg.id, 'Список всех сообщений: ' + (', '.join(all)), parse_mode=None)
        else: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!type'):
        msg.text = msg.text[5:]
        (
            threading.Thread(target=typeem, args=[msg, 0.1])
        ).start()
    elif msg.text == '!ava set day':
        try:
            if msg.reply_to_message is not None:
                if msg.reply_to_message.media is not None:
                    await bot.download_media(msg.reply_to_message, 'avas/day.png')
                else:
                    await bot.delete_messages(msg.chat.id, [msg.id])
            else:
                await bot.delete_messages(msg.chat.id, [msg.id])
        except ValueError: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!ava set night':
        try:
            if msg.reply_to_message is not None:
                if msg.reply_to_message.media is not None:
                    await bot.download_media(msg.reply_to_message, 'avas/night.png')
                else:
                    await bot.delete_messages(msg.chat.id, [msg.id])
            else:
                await bot.delete_messages(msg.chat.id, [msg.id])
        except ValueError: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!ava set default':
        try:
            if msg.reply_to_message is not None:
                if msg.reply_to_message.media is not None:
                    await bot.download_media(msg.reply_to_message, 'avas/default.png')
                else:
                    await bot.delete_messages(msg.chat.id, [msg.id])
            else:
                await bot.delete_messages(msg.chat.id, [msg.id])
        except ValueError: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!inline on':
        config.set('inline', 'enabled', 'true')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!inline off':
        config.set('inline', 'enabled', 'false')
        with open('config.ini', 'w') as configfile:  # save
            config.write(configfile)
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!ava on':
        config.set('avatar', 'dynamic', 'true')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!ava off':
        config.set('avatar', 'dynamic', 'false')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!ava set time day '):
        day_time = msg.text[13:]
        try: config.set('avatar', 'day_time', datetime.datetime.strptime(day_time, '%H:%M').strftime('%H:%M'))
        except ValueError: pass
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!ava set time night '):
        night_time = msg.text[15:]
        try: config.set('avatar', 'night_time', datetime.datetime.strptime(night_time, '%H:%M').strftime('%H:%M'))
        except ValueError: pass
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!ava get time':
        if config.get('avatar', 'dynamic') == 'true': await bot.edit_message_text(msg.chat.id, msg.id, f'Дневная аватарка с {config.get("avatar", "day_time")} до {config.get("avatar", "night_time")}\nНочная аватарка с {config.get("avatar", "night_time")} до {config.get("avatar", "day_time")}')
        else: await bot.edit_message_text(msg.chat.id, msg.id, 'Динамическая аватарка выключена')
    elif old_text != msg.text:
        await bot.edit_message_text(msg.chat.id, msg.id, msg.text)

    with open('config.ini', 'w') as configfile:  # save config
        config.write(configfile)

    if not ava_enabled:
        threading.Thread(target=ava).start()

def ava():
    while True:
        if config['avatar']['dynamic'] == 'true':
            if config['avatar']['dynamic'] == 'false': break
            global ava_enabled
            ava_enabled = False
            if time_in_range(datetime.datetime.strptime(config['avatar']['day_time'], '%H:%M').time(), datetime.datetime.strptime(config['avatar']['night_time'], '%H:%M').time(), datetime.datetime.now().time()):
                if config['do_not_change']['current_ava'] != '1':
                    bot.set_profile_photo(photo=config['avatar']['day'])
                    config.set('do_not_change', 'current_ava', '1')
            else:
                if config['do_not_change']['current_ava'] != '2':
                    bot.set_profile_photo(photo=config['avatar']['night'])
                    config.set('do_not_change', 'current_ava', '2')
        else:
            if config['do_not_change']['current_ava'] != '0':
                bot.set_profile_photo(photo=config['avatar']['default'])
                config.set('do_not_change', 'current_ava', '0')
        with open('config.ini', 'w') as configfile:  # save
            config.write(configfile)
        time.sleep(5)

def typeem(msg, dur):
    if len(msg.text) != 0:
        curr_text = ""
        for i in range(len(msg.text)):
            curr_text = curr_text[0:i-1]
            curr_text += msg.text[i]
            curr_text += '*' * (len(msg.text) - i - 1)
            if len(curr_text) != 0:
                bot.edit_message_text(msg.chat.id, msg.id, curr_text, parse_mode=enums.ParseMode.DISABLED)
            time.sleep(dur)


def time_in_range(start: datetime, end: datetime, current: datetime):
    return start <= current <= end


def db(command: str):
    database = sqlite3.connect('furatasa.sqlite')
    cursor = database.cursor()
    cursor.execute(command)
    database.commit()
    result = cursor.fetchall()
    database.close()
    return result


def main():
    try:
        print('Бот запущен\n', 'Нажмите ctrl+d для выхода', sep='')
        bot.run()
    except KeyboardInterrupt:
        print('До свидания!')
        sys.exit(0)
    return 0


if __name__ == '__main__': main()