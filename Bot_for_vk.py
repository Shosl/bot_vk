from os import environ
from datetime import datetime

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import telebot


def main():
    token = environ['TELEGRAM_TOKEN']
    token_vk = environ['VK_TOKEN']
    id_for_telegram = environ['CHAT_ID']

    bot = telebot.TeleBot(token)

    vk_session = vk_api.VkApi(token=token_vk)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    print('ok')
    
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
    
    def send_message(id_for_telegram, text_message):
        bot.send_message(chat_id=id_for_telegram, text=text_message)
        vk.status.set(text=text_message)
    
    for event in longpoll.listen():
        if event.type == VkEventType.USER_ONLINE:
            time_vk_server = vk.utils.getServerTime()
            online_time_user = datetime.fromtimestamp(time_vk_server).strftime('%H:%M:%S')
            text_message = 'Пользователь: {}({}). Онлайн с: {}. Время захода: {}'.format(get_fam_name(),
                                                                                 str(event.user_id),
                                                                                 get_platform_or_app(),
                                                                                 online_time_user)
            send_message(id_for_telegram, text_message)

        elif event.type == VkEventType.USER_OFFLINE:
            text_message = 'Пользователь: {}({}). Время ухода: {}'.format(get_fam_name(),
                                                                  str(event.user_id),
                                                                  get_last_seen())
            send_message(id_for_telegram, text_message)
            
        elif event.type == VkEventType.USER_TYPING:
            if event.from_user:
                text_message = 'Пользователь: {}({}) печатает'.format(get_fam_name(),
                                                              str(event.user_id))
                send_message(id_for_telegram, text_message)

        elif event.type == VkEventType.USER_TYPING_IN_CHAT:
            text_message = 'Пользователь: {}({}) печатает из беседы: {}'.format(get_fam_name(),
                                                                        str(event.user_id),
                                                                        str(event.chat_id))
            send_message(id_for_telegram, text_message)

        elif event.type == VkEventType.MESSAGE_NEW and not event.from_me:
            if event.from_user:
                text_message = 'Сообщение от: {}({}). Текст: {}'.format(get_fam_name(),
                                                                str(event.user_id),
                                                                event.text)
                bot.send_message(chat_id=id_for_telegram, text=text_message)
                
            elif event.from_chat:
                text_message = 'Сообщение от: {}({}). из беседы: {}. Текст: {}'.format(get_fam_name(),
                                                                               str(event.user_id),
                                                                               str(event.chat_id),
                                                                               event.text)
                bot.send_message(chat_id=id_for_telegram, text=text_message)
                
            elif event.from_group:
                text_message = 'Сообщение от группы: {}. Текст: {}'.format(str(event.group_id),
                                                                   event.text)
                send_message(id_for_telegram, text_message)


if __name__ == '__main__':
    main()
