try: import os, sys, random, sqlite3, datetime, threading, time, json
except ImportError as ie:
    print(f'Ошибка, какой-то из необходимых модулей не установился. Используйте python 3.10.\n{ie}')
    sys.exit(1)

try: from pyrogram import Client, filters, enums, types, errors
except ImportError:
    print('Ошибка, необходимо установить модуль pyrogram')
    sys.exit(1)
try: import messages as msgs
except ImportError:
    print(f'В папку с этим исполняемым файлом нужно положить messages.py')
    sys.exit(1)
try: import cards
except ImportError:
    print(f'В папку с этим исполняемым файлом нужно положить cards.py')
    sys.exit(1)
try: import configparser
except ImportError: import ConfigParser as configparser

config = configparser.ConfigParser()
config.read('config.ini')

bot = Client("my_account", api_id=config['pyrogram']['api_id'], api_hash=config['pyrogram']['api_hash'])

ava_enabled = False


def l(key: str) -> str:
    filename = config['locale']['file'].format(config['locale']['lang'])
    if not os.path.exists(filename):
        filename = 'locale.fallback.json'
        if not os.path.exists(filename):
            print(f'\n\nLanguageError - Not found {config["locale"]["file"].format(config["locale"]["lang"])} or local.fallback.json\n\n')
            sys.exit(1)
    with open(filename, 'r') as file:
        data = json.load(file)
        try:
            return data[key]
        except KeyError:
            print(f'\n\nLanguageError - Not found key {key} in {config["locale"]["file"].format(config["locale"]["lang"])}\n\n')
            sys.exit(1)

async def my_message(client: Client, msg: types.Message):
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
        if bot.me.username is not None: new_text = new_text.replace('%%my username%%', bot.me.username)
        if msg.chat.title is not None: new_text = new_text.replace('%%chat title%%', msg.chat.title)
        if msg.chat.username is not None: new_text = new_text.replace('%%chat username%%', msg.chat.username)

        result = db(f'select * from messages')
        if len(result) != 0:
            for _ in range(1, int(config['inline']['nesting'])):
                for i in result: new_text = new_text.replace(f'%{i[0]}%', i[1])

    old_text = msg.text
    msg.text = new_text

    if msg.text == "!whoami":
        await bot.edit_message_text(msg.chat.id, msg.id, f'{l("id")}: {bot.get_me().id}\n'
                                                         f'{l("username")}: @{bot.get_me().username}\n'
                                                         f'{l("name")} {bot.get_me().first_name}')
    elif msg.text == "!help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.HELP)
    elif msg.text == "!msg help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.MSGHELP)
    elif msg.text == "!ava help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.AVAHELP)
    elif msg.text == "!random help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.RANDOMHELP)
    elif msg.text == "!user help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.USERHELP)
    elif msg.text == "!inline help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.INLINEHELP)
    elif msg.text == "!furatasa help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.FURATASAHELP)
    elif msg.text == "!help help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.HELPHELP)
    elif msg.text == "!type help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.TYPEHELP)
    elif msg.text == "!creator help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.CREATORHELP)
    elif msg.text == "!whoami help": await bot.edit_message_text(msg.chat.id, msg.id, msgs.WHOAMIHELP)
    elif msg.text == "!chat":
        title = ''
        link = ''
        bio = ''
        description = ''
        count = ''
        if msg.chat.title is not None: title = f'{l("title")}: {msg.chat.title}\n'
        if msg.chat.username is not None: link = f'{l("link")}: https://t.me/{msg.chat.username}\n'
        if msg.chat.bio is not None: bio = f'{l("bio")}: {msg.chat.bio}\n'
        if msg.chat.description is not None: description = f'{l("description")}: {msg.chat.description}\n'
        if msg.chat.members_count is not None: count = f'{l("users-count")}: {msg.chat.members_count}\n'

        chat_type = 'Это '
        if msg.chat.type == enums.ChatType.PRIVATE:  chat_type += l("chat-private")
        elif msg.chat.type == enums.ChatType.BOT: chat_type += l("chat-bot")
        elif msg.chat.type == enums.ChatType.GROUP: chat_type += l("chat-group")
        elif msg.chat.type == enums.ChatType.SUPERGROUP: chat_type += l("chat-supergroup")
        elif msg.chat.type == enums.ChatType.CHANNEL: chat_type += l("chat-channel")

        permissions = ''
        if msg.chat.permissions is not None:
            permissions = f'{l("permissions")}:\n'
            if msg.chat.permissions.can_send_messages: permissions += f'\t- {l("permissions-send-message")}\n'
            if msg.chat.permissions.can_send_media_messages: permissions += f'\t- {l("permissions-send-media")}\n'
            if msg.chat.permissions.can_send_other_messages: permissions += f'\t- {l("permissions-send-sag-use-inline")}\n'
            if msg.chat.permissions.can_send_polls:  permissions += f'\t- {l("permissions-send-polls")}\n'
            if msg.chat.permissions.can_add_web_page_previews: permissions += f'\t- {l("permissions-add-web-preview")}\n'
            if msg.chat.permissions.can_change_info: permissions += f'\t- {l("permissions-change-group-settings")}\n'
            if msg.chat.permissions.can_invite_users: permissions += f'\t- {l("permissions-add-users")}\n'
            if msg.chat.permissions.can_pin_messages: permissions += f'\t- {l("permissions-pin-messages")}\n'
            if permissions == f'{l("permissions")}:\n': permissions = f'{l("permissions-nothing")}\n'
        reactions = '' if msg.chat.available_reactions is None else f'{l("permissions-available-reactions")}: ' + ', '.join(msg.chat.available_reactions)
        await bot.edit_message_text(msg.chat.id, msg.id, f'{l("id")}: {msg.chat.id}\n{title}{type}\n{link}{bio}{description}{reactions}{count}{l("verify") if msg.chat.is_verified else l("not-verify")}\n{permissions}')
    elif msg.text.startswith('!random dice'):
        try:
            number = int(msg.text[5:])
            await bot.edit_message_text(msg.chat.id, msg.id, str(random.randint(1, number)))
        except ValueError: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!random credit':
        cards_enum = [
            'VISA', 'MIR', 'MASTERCARD', 'MAESTRO', 'AMERICAN-EXPRESS', 'UNION-PAY'
        ]
        card = cards_enum[random.randint(0, len(cards_enum) - 1)]
        await bot.edit_message_text(msg.chat.id, msg.id, f'{cards.gen(key=card)} ({cards.randomDate()[1]}/{cards.randomDate()[0]}, {cards.randomCCV()})')
    elif msg.text.startswith('!msg read '):
        name = msg.text[10:]
        if msg.reply_to_message is not None and msg.reply_to_message.text is not None:
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
        db(f'delete from messages where name = \'{name}\'')
        db(f'select text from messages where name = \'{name}\'')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!msg info':
        if msg.reply_to_message is not None:
            username = '' if msg.reply_to_message.from_user.username is None else \
                f'{l("sender-username")}: @{msg.reply_to_message.from_user.username}\n'
            await bot.edit_message_text(msg.chat.id, msg.id, f'{l("id")}: {msg.reply_to_message.id}\n{l("sender-id")}: {msg.reply_to_message.from_user.id}\n{username}{l("time")}: {msg.date.strftime("%Y.%m.%d %H:%m:%s")}\n{l("msg-info-more-info")}')
        else: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!user info '):
        try:
            id = int(msg.text[11:])
            user = (await bot.get_users([id]))[0]
            contact = (l("user-info-contact") if user.is_contact else l("user-info-not-contact")) + '\n'
            mutualContact = (l("user-info-mutual") if user.is_mutual_contact else l("user-info-not-mutual")) + '\n'
            deleted = f'{l("user-info-deleted")}\n' if user.is_deleted else ''
            verify = (l("user-info-verify") if user.is_verified else l("user-info-not-verify")) + '\n'
            premium = (l("user-info-premium") if user.is_premium else l("user-info-not-premium")) + '\n'
            await bot.edit_message_text(msg.chat.id, msg.id, f'{l("id")}: {user.id}\n{l("username")}: {user.username}\n{l("name")}: {user.first_name}\n{contact}{mutualContact}{deleted}{verify}{premium}')
        except Exception: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!msg all':
        result = db(f'select name from messages')
        if len(result) != 0:
            all_msgs = []
            for i in result: all_msgs.append(i[0])
            await bot.edit_message_text(msg.chat.id, msg.id, f'{l("all-messages")}: ' + (', '.join(all_msgs)), parse_mode=None)
        else: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!type'):
        msg.text = msg.text[5:]
        threading.Thread(target=typeem, args=[msg, 0.1]).start()
    elif msg.text == '!ava set day':
        try:
            if msg.reply_to_message is not None and msg.reply_to_message.media is not None:
                await bot.download_media(msg.reply_to_message, 'avas/day.png')
                config.set('do_not_change', 'current_ava', '')
        except ValueError: pass
        except errors.exceptions.bad_request_400.PhotoCropSizeSmall: pass
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!ava set night':
        try:
            if msg.reply_to_message is not None and msg.reply_to_message.media is not None:
                await bot.download_media(msg.reply_to_message, 'avas/night.png')
                config.set('do_not_change', 'current_ava', '')
        except ValueError: pass
        except errors.exceptions.bad_request_400.PhotoCropSizeSmall: pass
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!ava set default':
        try:
            if msg.reply_to_message is not None and msg.reply_to_message.media is not None:
                await bot.download_media(msg.reply_to_message, 'avas/default.png')
                config.set('do_not_change', 'current_ava', '')
        except ValueError: pass
        except errors.exceptions.bad_request_400.PhotoCropSizeSmall: pass
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!inline on':
        config.set('inline', 'enabled', 'true')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!inline off':
        config.set('inline', 'enabled', 'false')
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
        if config.get('avatar', 'dynamic') == 'true': await bot.edit_message_text(msg.chat.id, msg.id, f'{l("day-ava-from")} {config.get("avatar", "day_time")} {l("to")} {config.get("avatar", "night_time")}\n{l("night-ava-from")} {config.get("avatar", "night_time")} {l("to")} {config.get("avatar", "day_time")}')
        else: await bot.edit_message_text(msg.chat.id, msg.id, l("dynamic-ava-not-enabled"))
    elif msg.text.startswith('!msg auto add '):
        if len(msg.text[14:].split(sep=' ')) == 3:
            name = msg.text[14:].split(sep=' ')[0]
            name1 = msg.text[14:].split(sep=' ')[1]
            name2 = msg.text[14:].split(sep=' ')[2]

            db(f'insert into autoresponder(name, entrance, output, whitelist, blacklist, usewhitelist) values("{name}","{name1}","{name2}","","",0)')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!msg auto remove '):
        if len(msg.text[17:].split(sep=' ')) != 0:
            name = msg.text[17:].split(sep=' ')[0]
            db(f'delete from autoresponder where name = "{name}"')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!msg auto all':
        result = db('select name from autoresponder')
        if len(result) != 0:
            names = []
            for i in result:
                names.append(i[0])
            await bot.edit_message_text(msg.chat.id, msg.id, ', '.join(names))
        else: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!msg auto get '):
        name = msg.text[14:]
        result: list = db(f'select * from autoresponder where name = "{name}"')
        if len(result) != 0:
            info = f'{l("title")}: {name}\n'
            info += f'{l("phrase-in")}: {result[0][1]}\n'
            info += f'{l("phrase-out")}: {result[0][2]}\n'
            if result[0][5] == 1:
                if result[0][3] != '':
                    info += f'{l("whitelist")}: {result[0][3]}\n'
            else:
                if result[0][4] != '':
                    info += f'{l("blacklist")}: {result[0][4]}\n'
            await bot.edit_message_text(msg.chat.id, msg.id, info)
        else: await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!msg auto '):
        args = msg.text[10:].split(sep=' ')
        if len(args) == 4:
            name = args[0]
            if args[2] == 'wlist':
                result = db(f'select whitelist from autoresponder where name = "{name}"')
                if len(result) != 0:
                    whitelist: list = result[0][0].split(sep=',')
                    if args[1] == 'add':
                        whitelist.append(args[3])
                    elif args[1] == 'remove':
                        whitelist.remove(args[3])
                    try: whitelist.remove('')
                    except ValueError: pass
                    db(f'update autoresponder set whitelist = "{",".join(whitelist)}" where name = "{name}"')
            elif args[2] == 'blist':
                result = db(f'select blacklist from autoresponder where name = "{name}"')
                if len(result) != 0:
                    blacklist: list = result[0][0].split(sep=',')
                    if args[1] == 'add':
                        blacklist.append(args[3])
                    elif args[1] == 'remove':
                        blacklist.remove(args[3])
                    try: whitelist.remove('')
                    except ValueError: pass
                    db(f'update autoresponder set blacklist = "{",".join(blacklist)}" where name = "{name}"')
            elif args[1] == 'list':
                if args[2] == 'use':
                    if args[3] == 'wlist':
                        db(f'update autoresponder set usewhitelist = 1 where name = "{name}"')
                        print('wlist')
                    elif args[3] == 'blist':
                        print('blist')
                        db(f'update autoresponder set usewhitelist = 0 where name = "{name}"')
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text.startswith('!user block '):
        user = msg.text[11:]
        try: await bot.block_user(int(user))
        except ValueError: await bot.block_user(user)
        except errors.exceptions.bad_request_400.UsernameNotOccupied: pass
    elif msg.text.startswith('!user unblock '):
        user = msg.text[13:]
        try: await bot.unblock_user(int(user))
        except ValueError: await bot.unblock_user(user)
        except errors.exceptions.bad_request_400.UsernameNotOccupied: pass
    elif msg.text == '!creator':
        await bot.send_message("mrybs1", msgs.TOCREATOR)
        await bot.delete_messages(msg.chat.id, [msg.id])
    elif msg.text == '!furatasa channel': await (await bot.get_chat('furatasa')).join()
    elif msg.text == '!furatasa ideas': await (await bot.get_chat('furatasa_ideas')).join()
    elif old_text != msg.text: await bot.edit_message_text(msg.chat.id, msg.id, msg.text)

    with open('config.ini', 'w') as configfile: config.write(configfile)
    if not ava_enabled: threading.Thread(target=ava).start()


async def autoresponder(client: Client, msg: types.Message):
    if msg.chat.type != enums.ChatType.PRIVATE and msg.chat.type != enums.ChatType.BOT:
        if msg.reply_to_message is not None:
            if msg.reply_to_message.from_user is not None:
                if msg.reply_to_message.from_user == bot.me: pass
                else: return
            else: return
        else: return
    else: pass

    result = db('select * from autoresponder')
    if len(result) != 0:
        for i in result:
            entrance_name: str = i[1]
            output_name: str = i[2]
            whitelist_str: str = i[3]
            blacklist_str: str = i[4]
            use_whitelist: int = i[5]

            whitelist: list = whitelist_str.split(sep=',')
            blacklist: list = blacklist_str.split(sep=',')

            send: bool = True

            result_messages: list = db(f'select text from messages where name = "{entrance_name}"')
            if len(result_messages) == 0: return
            entrance: str = result_messages[0][0]

            result_messages: list = db(f'select text from messages where name = "{output_name}"')
            if len(result_messages) == 0: return
            output: str = result_messages[0][0]

            if use_whitelist == 0:
                if len(blacklist) != 0:
                    send = True
                    for j in blacklist:
                        if j == msg.from_user.id or j == msg.from_user.username: send = False
            elif use_whitelist == 1:
                if len(whitelist) != 0:
                    send = False
                    for j in whitelist:
                        if j == msg.from_user.id or j == msg.from_user.username: send = True

            if not send: break

            if entrance.lower() in msg.text.lower():
                await bot.send_message(msg.chat.id, output)
                break


@bot.on_message()
async def message(client: Client, msg: types.Message):
    if msg.from_user is not None and msg.from_user.id == bot.me.id: await my_message(client, msg)
    else: await autoresponder(client, msg)


@bot.on_edited_message()
async def edit_command(client: Client, msg: types.Message):
    if msg.from_user == bot.me:
        await my_message(client, msg)


def ava():
    while True:
        global ava_enabled
        ava_enabled = False
        if config['avatar']['dynamic'] == 'true':
            if time_in_range(datetime.datetime.strptime(config['avatar']['day_time'], '%H:%M').time(),
                             datetime.datetime.strptime(config['avatar']['night_time'], '%H:%M').time(),
                             datetime.datetime.now().time()):
                if config['do_not_change']['current_ava'] != '1':
                    bot.set_profile_photo(photo=config['avatar']['day'])
                    config.set('do_not_change', 'current_ava', '1')
            elif config['do_not_change']['current_ava'] != '2':
                bot.set_profile_photo(photo=config['avatar']['night'])
                config.set('do_not_change', 'current_ava', '2')
        elif config['do_not_change']['current_ava'] != '0':
            bot.set_profile_photo(photo=config['avatar']['default'])
            config.set('do_not_change', 'current_ava', '0')
        with open('config.ini', 'w') as configfile: config.write(configfile)
        time.sleep(5)

def typeem(msg, dur):
    if len(msg.text) != 0:
        curr_text = ""
        for i in range(len(msg.text)):
            curr_text = curr_text[0:i-1]
            curr_text += msg.text[i]
            curr_text += '*' * (len(msg.text) - i - 1)
            if len(curr_text) == 0: continue
            bot.edit_message_text(msg.chat.id, msg.id, curr_text, parse_mode=enums.ParseMode.DISABLED)
            time.sleep(dur)


def time_in_range(start: datetime, end: datetime, current: datetime):
    return start <= current <= end


def db(command: str):
    database = sqlite3.connect(config['database']['file'])
    cursor = database.cursor()
    cursor.execute(command)
    database.commit()
    result = cursor.fetchall()
    database.close()
    return result


def main():
    db('create table if not exists messages(name text,text text,type int)')
    db('create table if not exists autoresponder(name text,entrance text,output text,whitelist text,blacklist text,usewhitelist shortint)')
    try:
        print(f'{l("bot-started")}\n', l("press-to-exit"), sep='')
        bot.run()
    except KeyboardInterrupt: pass
    print(l("goodbye"))
    return 0


if __name__ == '__main__': main()
