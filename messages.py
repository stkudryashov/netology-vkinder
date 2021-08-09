import vk_api
import config
import time

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from pprint import pprint


def user_search(vk, user_id):
    vk_user_session = vk_api.VkApi(token=config.user_token)
    vk_user = vk_user_session.get_api()

    vk.messages.send(
        peer_id=user_id,
        random_id=get_random_id(),
        message="Запускаю поиск.."
    )

    result = vk_user.users.search(
        count=10,
        fields=['photo_id', 'sex', 'bdate', 'city'],
        sex=1,
        age_from=20,
        age_to=30,
        has_photo=1
    )

    pprint(result)


def log_messages(user_text, user_id, event):
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


def main():
    vk_session = vk_api.VkApi(token=config.access_token)

    this_poll = VkBotLongPoll(vk_session, config.group_id)
    vk = vk_session.get_api()

    while True:
        try:
            for event in this_poll.listen():
                log_messages(event.obj.text, event.obj.peer_id, event)

                if event.type == VkBotEventType.MESSAGE_NEW:
                    user_text = event.obj.text.lower()
                    user_id = event.obj.peer_id

                    if user_text == 'начать':
                        user_search(vk, user_id)
        except Exception as exception:
            print(exception)
            time.sleep(10)


if __name__ == '__main__':
    main()
