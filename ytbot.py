import os
import re
import telebot
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
from telebot.types import Message
from telebot import types

bot = telebot.TeleBot("TOKEN")


@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.chat.id,
                     text=f'Привет, {message.from_user.first_name}. Я бот, который может скачать видео из YouTube и '
                          f'отправить mp3 и mp4 файлы созданные из этого видео. Бот не имеет возможности работать с '
                          f'видео из YouTube shorts')


def is_youtube_video_link(url):
    if ("music.youtube" not in url) and ("youtu" in url):
        return True
    else:
        return False


def keyboard(message: Message, name_file):
    keys = types.ReplyKeyboardMarkup(True)
    keys.add("MP3")
    keys.add("MP4")
    keys.add("MP4 & MP3")
    bot.send_message(message.chat.id, text="Какой формат данных вам нужен?", reply_markup=keys)
    bot.register_next_step_handler(message, send, name_file)


def send(message: Message, yt):
    if message.text == "MP3":
        bot.send_message(message.chat.id, text="Подготавливаем файл...")
        bot.send_audio(message.chat.id, audio=open(f'{yt}.mp3', 'rb'))
        bot.send_message(message.chat.id, text="Для повторной работы отправьте ссылку")
        os.remove(f'{yt}.mp3')
    elif message.text == "MP4":
        bot.send_message(message.chat.id, text="Подготавливаем файл...")
        bot.send_video(message.chat.id, video=open(f'{yt}.mp4', 'rb'))
        bot.send_message(message.chat.id, text="Для повторной работы отправьте ссылку")
        os.remove(f'{yt}.mp4')
    elif message.text == "MP4 & MP3":
        bot.send_message(message.chat.id, text="Подготавливаем файлы...")
        bot.send_video(message.chat.id, video=open(f'{yt}.mp4', 'rb'))
        bot.send_audio(message.chat.id, audio=open(f'{yt}.mp3', 'rb'))
        bot.send_message(message.chat.id, text="Для повторной работы отправьте ссылку")
        os.remove(f'{yt}.mp4')
        os.remove(f'{yt}.mp3')
    else:
        bot.send_message(message.chat.id, text="Неверный формат данных")
        keyboard(message, yt)


def download_video(message: Message):
    bot.send_message(message.chat.id, text="Ожидайте, бот начал работу")
    link = message.text
    yt = YouTube(link)
    stream = yt.streams.get_highest_resolution()

    clean_title = re.sub(r'[<>:"/|?*]', '', yt.title)

    stream.download(output_path='.', filename=f'{clean_title}.mp4')
    video = VideoFileClip(f'{clean_title}.mp4')
    video.audio.write_audiofile(f'{clean_title}.mp3')

    video.close()

    keyboard(message, clean_title)


@bot.message_handler(content_types=["text"])
def answer(message: Message):
    if is_youtube_video_link(message.text):
        download_video(message)
    else:
        bot.send_message(
            message.chat.id,
            text="Неверная ссылка. Для корректной работы пришлите ссылку на видео с YouTube"
        )


if __name__ == "__main__":
    bot.polling(none_stop=True)