"""
This is a detailed example using almost every command of the API
"""

import telebot
import soundfile as sf
import bottoken
import subprocess
import os

MYTOKEN = bottoken.MTOKEN

blockedUsers = []
knownUsers = []  # todo: save these in a file,
userStep = {}  # so they won't reset every time the bot restarts

commands = {  # command description used in the "help" command
              'help': 'Gives you information about the available commands',
}


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        print m.content_type
        if m.content_type == 'text':
            # print the sent message to the console
            print str(m.chat.first_name) + \
                " [" + str(m.chat.id) + "]: " + m.text

bot = telebot.TeleBot(MYTOKEN)
bot.set_update_listener(listener)  # register listener


@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    bot.send_message(cid, "Welcome to the Audio Bot!")
    bot.send_message(cid, "Just send me a voice msg")


# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "hi")
def command_text_hi(m):
    bot.send_message(m.chat.id, "I love you too!")


class tempfile:
    """ Context for temporary file.
    Will find a free temporary filename upon entering
    and will try to delete the file on leaving

    """
    def __init__(self, suffix):
        self.suffix = suffix

    def __enter__(self):
        import tempfile as tmp
        self.fd, self.name = tmp.mkstemp(suffix=self.suffix)
        os.close(self.fd)
        return self.name

    def __exit__(self, type, value, traceback):
        try:
            os.remove(self.name)
        except OSError as e:
            if e.errno == 2:
                pass
            else:
                raise e


@bot.message_handler(func=lambda message: True, content_types=['voice'])
def command_default(m):
    # this is the standard reply to a normal message
    file_info = bot.get_file(m.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with tempfile('.opus') as opus_file:
        with tempfile('.wav') as wav_file:
            with open(opus_file, 'wb') as of:
                of.write(downloaded_file)

            subprocess.call(['ffmpeg', '-y', '-i', opus_file, wav_file])

            audio, samplerate = sf.read(wav_file)

            try:
                bot.send_message(
                    m.chat.id, "Received %d samples" % audio.shape[0]
                )
            except ValueError as e:
                bot.send_message(m.chat.id, e.message)

bot.polling()
