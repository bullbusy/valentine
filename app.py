from models import *
import config
import phrases
import drawer

from os import listdir
from aiogram import Bot, Dispatcher, executor
from aiogram.types import *
from aiogram.types import input_file
from datetime import datetime, timedelta

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot=bot)


async def create_delete_btn(val_id: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(text='Удалить валенитнку', callback_data=f'delete_valentine {val_id}')


def check_time_callback(f):
    async def wrapper(message: CallbackQuery):
        try:
            user = UserModel.get(id=message.message.chat.id)
        except UserModel.DoesNotExist:
            return await f(message)
        if user.next_msg < datetime.now():
            user.next_msg = datetime.now() + timedelta(seconds=3)
        else:
            return
        return await f(message)
    return wrapper


def check_time_msg(f):
    async def wrapper(message: Message):
        try:
            user = UserModel.get(id=message.chat.id)
        except UserModel.DoesNotExist:
            return await f(message)
        if user.next_msg < datetime.now():
            user.next_msg = datetime.now() + timedelta(seconds=3)
        else:
            return
        return await f(message)
    return wrapper


async def check_if_user_registered(message: Message) -> UserModel:
    try:
        return UserModel.get(id=message.chat.id)
    except UserModel.DoesNotExist:
        return UserModel.create(id=message.chat.id, username=message.from_user.username)


async def get_all_pictures_by_theme(theme_name: str, chat_id: int) -> InlineKeyboardMarkup:
    images = sorted(listdir(f'templates/{theme_name}'), key=lambda x: int(x.split('.')[0]))
    data = [[], []]
    for image in images:
        data[0].append(InputMediaPhoto(open(f'templates/{theme_name}/{image}', 'rb')))
        data[1].append(InlineKeyboardButton(text=image.split('.')[0], callback_data=f'choose_image {image}'))
    await bot.send_media_group(chat_id, data[0])
    markup = InlineKeyboardMarkup()
    markup.add(*data[1])
    return markup


async def set_valentine_topic(message: Message) -> list:
    user = UserModel.get(id=message.chat.id)
    valentine = ValentineModel(id=user.status.split()[-1])
    try:
        listdir(f'templates/{message.text}')
    except FileNotFoundError:
        return ['Такой темы не существует', None]
    valentine.theme = message.text
    user.status = f'choose_valentine_image {valentine.id}'
    user.save()
    valentine.save()
    return ['Выберите картинку', await get_all_pictures_by_theme(valentine.theme, message.chat.id)]


async def choose_valentine_image(message: CallbackQuery) -> list:
    for i in range(1, 11):
        await bot.delete_message(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id - i
        )
    user = UserModel.get(id=message.message.chat.id)
    valentine = ValentineModel.get(id=user.status.split()[-1])
    valentine.file = f'{message.data.split()[-1]}'
    user.status = f'set_valentine_initiator_pseudo {valentine.id}'
    user.save()
    valentine.save()
    markup = InlineKeyboardMarkup()
    markup.add(await create_delete_btn(valentine.id))
    return ['Как вас называть? (Любой текст)', markup]


async def set_valentine_initiator_pseudo(message: Message) -> list:
    u = UserModel.get(id=message.chat.id)
    val = ValentineModel.get(id=u.status.split()[-1])
    val.initiator_pseudo = message.text
    u.status = f'set_valentine_receiver_pseudo {val.id}'
    u.save()
    val.save()
    markup = InlineKeyboardMarkup()
    markup.add(await create_delete_btn(val.id))
    return ['Как называть получателя? (Любой текст)', markup]


async def set_valentine_receiver_pseudo(message: Message) -> list:
    u = UserModel.get(id=message.chat.id)
    val = ValentineModel.get(id=u.status.split()[-1])
    val.receiver_pseudo = message.text
    u.status = f'set_valentine_receiver {val.id}'
    u.save()
    val.save()
    markup = InlineKeyboardMarkup()
    markup.add(await create_delete_btn(val.id))
    return ['Отправьте тег получателя', markup]


async def draw_valentine(val_id: int) -> str:
    val = ValentineModel.get(id=val_id)
    path = f'templates/{val.theme}/{val.file}'
    val.full_path = drawer.draw(path, val.initiator_pseudo, val.receiver_pseudo)
    val.save()
    return val.full_path


async def set_valentine_receiver(message: Message) -> list:
    u = UserModel.get(id=message.chat.id)
    val = ValentineModel.get(id=u.status.split()[-1])
    val.receiver = message.text
    u.status = 'main_menu'
    u.save()
    val.save()
    path = await draw_valentine(val.id)
    print(path)
    await bot.send_photo(
        chat_id=config.CHAT,
        photo=InputFile(path),
        caption=f'Валентинка від [{u.id}](tg://user?id={u.id}), відправити {val.receiver}',
        parse_mode='Markdown'
    )
    return ['Для отправки ещё одной валентинки напиши /start', None]


async def delete_valentine(message: CallbackQuery) -> list:
    val = ValentineModel.get(id=message.data.split()[-1])
    u = val.initiator
    u.status = 'main_menu'
    u.save()
    val.delete_instance()
    return [phrases.start, config.choose_type]


@dp.message_handler(commands=['start'])
@check_time_msg
async def start(message: Message):
    if message.chat.id < 0:
        return
    user = await check_if_user_registered(message)
    for val in user.valentines:
        if not val.full_path:
            val.delete_instance()
    v = ValentineModel.create(initiator=user)
    user.status = f'set_valentine_topic {v.id}'
    user.save()
    await bot.send_message(
        chat_id=user.id,
        text=phrases.start,
        reply_markup=config.choose_type
    )


@dp.message_handler()
@check_time_msg
async def process_text(message: Message):
    if message.chat.id < 0:
        return
    try:
        user = UserModel.get(id=message.chat.id)
    except UserModel.DoesNotExist:
        return
    data = await eval(f'{user.status.split()[0]}(message)')
    await bot.send_message(
        chat_id=user.id,
        text=data[0],
        reply_markup=data[1]
    )


@dp.callback_query_handler()
@check_time_callback
async def process_callback(message: CallbackQuery):
    await bot.delete_message(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id
    )
    user = UserModel.get(id=message.message.chat.id)
    if message.data.startswith('delete_valentine'):
        data = await delete_valentine(message)
        await bot.send_message(
            chat_id=message.message.chat.id,
            text=data[0],
            reply_markup=data[1]
        )
        return
    data = await eval(f'{user.status.split()[0]}(message)')
    await bot.send_message(
        chat_id=user.id,
        text=data[0],
        reply_markup=data[1]
    )


executor.start_polling(dp, skip_updates=True)
