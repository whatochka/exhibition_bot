import os
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from app.utils.audio import convert_to_ogg_voice


async def handle_voice_input(message: Message, state: FSMContext, bot: Bot, finish_callback):
    """
    Обрабатывает голосовое сообщение, mp3/wav или текст "нет".
    После обработки вызывает `finish_callback(message, state)`
    """

    if message.voice:
        file_id = message.voice.file_id

    elif message.audio and message.audio.mime_type in ("audio/mpeg", "audio/wav"):
        # Скачиваем файл
        file = await bot.download(message.audio.file_id)
        input_format = "mp3" if "mpeg" in message.audio.mime_type else "wav"
        ogg_path = convert_to_ogg_voice(file.read(), input_format=input_format)

        with open(ogg_path, "rb") as f:
            sent = await bot.send_voice(chat_id=message.chat.id, voice=f)

        file_id = sent.voice.file_id
        os.remove(ogg_path)

    elif message.text and message.text.lower() == "нет":
        file_id = None

    else:
        await message.answer(
            "❗ Отправьте голосовое сообщение, mp3/wav-файл или напишите <b>нет</b>.",
            parse_mode="HTML"
        )
        return

    await state.update_data(voice=file_id)
    await finish_callback(message, state)
