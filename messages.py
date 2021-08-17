import vk_api
import config
import random
import time

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from log_messages.log_messages import logging
from vk_kinder.vk_kinder import VKinder

from models import Session, User, Views
from sqlalchemy.sql import exists


db_session = Session()


def state_manager(vk, user, user_text):
    keyboard = VkKeyboard(inline=True)

    if user.state == 'search_age_from':
        if not user_text.isdigit():
            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='Ты вводишь не число'
            )
        else:
            user.search_age_from = int(user_text)
            user.state = 'search_age_to'
            db_session.commit()

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='До какого возраста ищем?'
            )
    elif user.state == 'search_age_to':
        if not user_text.isdigit():
            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='Ты вводишь не число'
            )
        elif int(user_text) < user.search_age_from:
            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='Максимальный возраст не может быть меньше минимального'
            )
        else:
            keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)

            user.search_age_to = int(user_text)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Сохранено'
            )

            user.state = 'default'
            db_session.commit()
    elif user.state == 'search_sex':
        if user_text in ['парни', 'девушки', 'не имеет значения']:
            if user_text == 'парни':
                user.search_sex = 2
            elif user_text == 'девушки':
                user.search_sex = 1
            elif user_text == 'не имееет значения':
                user.search_sex = 0

            keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Сохранено'
            )

            user.state = 'default'
            db_session.commit()
        else:
            keyboard.add_button('Парни', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Девушки', color=VkKeyboardColor.PRIMARY)

            keyboard.add_line()
            keyboard.add_button('Не имеет значения', color=VkKeyboardColor.PRIMARY)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Выбери один из вариантов'
            )
    elif user.state == 'search_status':
        if user_text in ['не женат (не замужем)', 'все сложно', 'в активном поиске']:
            if user_text == 'не женат (не замужем)':
                user.search_status = 1
            elif user_text == 'все сложно':
                user.search_status = 5
            elif user_text == 'в активном поиске':
                user.search_status = 6

            keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Сохранено'
            )

            user.state = 'default'
            db_session.commit()
        else:
            keyboard.add_button('Не женат (Не замужем)', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Все сложно', color=VkKeyboardColor.PRIMARY)

            keyboard.add_line()
            keyboard.add_button('В активном поиске', color=VkKeyboardColor.PRIMARY)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Выбери один из вариантов'
            )


def search_settings(vk, user, user_text):
    keyboard = VkKeyboard(inline=True)

    if user_text == 'настройки поиска':
        keyboard.add_button('Семейное положение', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Пол', color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('Возраст', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Настройки поиска'
        )
    elif user_text == 'возраст':
        user.state = 'search_age_from'
        db_session.commit()

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='С какого возраста ищем?'
        )
    elif user_text == 'пол':
        user.state = 'search_sex'
        db_session.commit()

        keyboard.add_button('Парни', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Девушки', color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('Не имеет значения', color=VkKeyboardColor.PRIMARY)

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Кто тебя интересует?'
        )
    elif user_text == 'семейное положение':
        user.state = 'search_status'
        db_session.commit()

        keyboard.add_button('Не женат (Не замужем)', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Все сложно', color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('В активном поиске', color=VkKeyboardColor.PRIMARY)

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Семейное положение для поиска'
        )


def user_search(vk, user, session):
    kinder = VKinder(vk, session)
    keyboard = VkKeyboard(inline=True)

    keyboard.add_button('Дальше', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Посмотреть страницу', color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()
    keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)

    result = kinder.search(user)
    viewed = [view.get() for view in user.user_views]
    filtered = [user for user in result if user['is_closed'] is False and user['id'] not in viewed]

    var = random.choice(filtered)
    message = f"{var['first_name']} {var['last_name']}, {var['bdate']}, {var['city']['title']}"

    user.current_page = var['id']

    db_session.add(Views(user.user_id, var['id']))
    db_session.commit()

    vk.messages.send(
        peer_id=user.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=message,
        attachment=kinder.photos(var['id'])
    )


def main():
    vk_session = vk_api.VkApi(token=config.access_token)

    this_poll = VkBotLongPoll(vk_session, config.group_id)
    vk = vk_session.get_api()

    user_session = vk_api.VkApi(token=config.user_token)
    session = user_session.get_api()

    while True:
        try:
            for event in this_poll.listen():
                logging(event.obj.text, event.obj.peer_id, event)

                if event.type == VkBotEventType.MESSAGE_NEW:
                    user_text = event.obj.text.lower()
                    user_id = event.obj.peer_id

                    user = User(user_id)

                    if db_session.query(exists().where(User.user_id == user_id)).scalar():
                        user = db_session.query(User).get(user_id)
                    else:
                        db_session.add(user)
                        db_session.commit()

                    if user.state != 'default':
                        state_manager(vk, user, user_text)

                    if user_text in ['дальше', 'начать', 'начать поиск']:
                        user_search(vk, user, session)
                    elif user_text in ['настройки поиска', 'возраст', 'пол', 'семейное положение']:
                        search_settings(vk, user, user_text)
                    elif user_text == 'посмотреть страницу':
                        vk.messages.send(
                            peer_id=user.user_id,
                            random_id=get_random_id(),
                            message=f'vk.com/id{user.current_page}'
                        )
                    else:
                        vk.messages.send(
                            peer_id=user.user_id,
                            random_id=get_random_id(),
                            message=f'Для взаимодействия с ботом используй кнопки'
                        )
        except Exception as exception:
            print(exception)
            time.sleep(5)
