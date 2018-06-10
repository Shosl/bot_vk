import os
from datetime import datetime

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import telebot
from telebot import apihelper


def main():
    token = os.environ['TELEGRAM_TOKEN']
    token_vk = os.environ['VK_TOKEN']
    id_for_telegram = os.environ['CHAT_ID']

    bot = telebot.TeleBot(token)
    apihelper.proxy = {'https': 'socks5://telegram:telegram@frkw.cf:1080'}

    vk_session = vk_api.VkApi(token=token_vk)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    def get_profile_user(field):
        return vk.users.get(user_id=event.user_id, fields=field)

    def get_last_seen():
        return datetime.fromtimestamp(get_profile_user('last_seen')
                                      [0]['last_seen']['time']).strftime('%H:%M:%S')

    def get_platform_or_app():
        try:
            return vk.apps.get(app_id=get_profile_user('online')[0]['online_app']).get('items')[0]['title']
        except KeyError:
            return str(event.platform)[11:].capitalize()

    def get_fam_name():
        last_name = get_profile_user('last_name')[0]['last_name']
        first_name = get_profile_user('first_name')[0]['first_name']
        return last_name + ' ' + first_name

    for event in longpoll.listen():
        if event.type == VkEventType.USER_ONLINE:
            time_vk_server = vk.utils.getServerTime()
            online_time_user = datetime.fromtimestamp(time_vk_server).strftime('%H:%M:%S')
            text = 'Пользователь: {}({}). Онлайн с: {}. Время захода: {}'.format(get_fam_name(),
                                                                                 str(event.user_id),
                                                                                 get_platform_or_app(),
                                                                                 online_time_user)
            bot.send_message(chat_id=id_for_telegram, text=text)

        elif event.type == VkEventType.USER_OFFLINE:
            text = 'Пользователь: {}({}). Время ухода: {}'.format(get_fam_name(),
                                                                  str(event.user_id),
                                                                  get_last_seen())
            bot.send_message(chat_id=id_for_telegram, text=text)

        elif event.type == VkEventType.MESSAGE_NEW and not event.from_me:
            if event.from_user:
                text = 'Сообщение от: {}. Текст: {}'.format(str(event.user_id),
                                                            event.text)
                bot.send_message(chat_id=id_for_telegram, text=text)
            elif event.from_chat:
                text = 'Сообщение от: {}. из беседы: {}. Текст: {}'.format(str(event.user_id),
                                                                           str(event.chat_id),
                                                                           event.text)
                bot.send_message(chat_id=id_for_telegram, text=text)
            elif event.from_group:
                text = 'Сообщение от группы: {}. Текст: {}'.format(str(event.group_id),
                                                                   event.text)
                bot.send_message(chat_id=id_for_telegram, text=text)


if __name__ == '__main__':
    main()
