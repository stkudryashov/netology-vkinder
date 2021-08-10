from vk_api.bot_longpoll import VkBotEventType


def logging(user_text, user_id, event):
    if event.type == VkBotEventType.MESSAGE_NEW:
        print()

        print('Новое сообщение:')

        print('Для меня от ', end='')

        print(user_id)

        print('Текст:', user_text)
    elif event.type == VkBotEventType.MESSAGE_REPLY:
        print()

        print('Новое сообщение:')

        print('От меня для ', end='')

        print(user_id)

        print('Текст:', user_text)