import datetime
import re
from collections import defaultdict
from string import punctuation
import langdetect
from graphics import draw_single_res, draw_circle_graph
from dateutil import parser


PUKIN_STARTED_WAR = datetime.date(year=2022, month=2, day=24)
ALCO_LIST = ["пив", "водк", "вино", "ликер", "виски", "сидр"]
alco_list_conversion = {
    "пив": "пиво",
    "водк": "водка",
}
NEOLOGISMS = ["кек", "лол", "рофл", "кринж", ]


class MessageHandler:
    _next_handler = None

    def set_next(self, handler):
        self._next_handler = handler

    def handle(self, message: dict):
        return self._next_handler.handle(message) if self._next_handler else None

    def response(self):
        return self._next_handler.response() if self._next_handler else None


class AnyMessageHandler(MessageHandler):
    def __init__(self):
        self.any_message_per_hour = defaultdict(int)
        self.fwd_message = defaultdict(int)

    def handle(self, message: dict) -> None:

        hour = int(re.search("\s[0-9]+", message["date"]).group(0).lstrip())
        self.any_message_per_hour[f"{hour}-{hour + 1}"] += 1
        fwd_message_key = "forwarded" if message["fwd_from"] else "not forwarded"
        self.fwd_message[fwd_message_key] += 1
        super().handle(message)

    def response(self) -> None:
        for res in [
            (
                self.any_message_per_hour,
                "any message hour",
                "amount",
                "amount of all messages based on the hour of day",
                True,
            ),
        ]:
            draw_single_res(*res)

        for res in [(self.fwd_message, True)]:
            draw_circle_graph(*res)

        super().response()


class VoiceHandler(MessageHandler):
    def __init__(self):
        self.length_voice = defaultdict(int)
        self.voices_per_hour = defaultdict(int)

    def handle(self, message):
        if message["type"] == "voice":
            self.length_voice[message["duration"]] += 1
            hour = int(re.search("\s[0-9]+", message["date"]).group(0).lstrip())
            self.voices_per_hour[f"{hour}-{hour + 1}"] += 1
        else:
            super().handle(message)

    def response(self) -> None:
        for res in [
            (
                self.length_voice,
                "voice duration",
                "amount",
                "amount of voices based on their duration",
                True,
            ),
            (
                self.voices_per_hour,
                "voice hour",
                "amount",
                "amount of voices based on the hour of day",
                True,
            ),
        ]:
            draw_single_res(*res)

        super().response()


class TextHandler(MessageHandler):
    def __init__(self):
        self.length_message: defaultdict = defaultdict(int)
        self.words_amount: defaultdict = defaultdict(int)
        self.messages_per_hour = defaultdict(int)
        self.symbol_amount = defaultdict(int)
        self.punctuation = defaultdict(int)
        self.upper_lower = defaultdict(int)  # message
        self.upper_lower_sym = defaultdict(int)  # syms
        self.languages = defaultdict(int)
        self.messages_by_lang_war = defaultdict(int)
        self.messages_by_lang_before_war = defaultdict(int)
        self.major_alcocholics = defaultdict(int)  # amount of alco mentioned by user
        self.major_alco_mentioned = defaultdict(int)  # amount of mentions of certain type of alco
        self.neologisms_mentioned = defaultdict(int)

    def handle(self, message: dict) -> None:
        if message["type"] == "text":
            text = message["message"]

            if len(alco_mentioned := [alco for alco in ALCO_LIST if alco in text]):
                self.major_alcocholics[message["id"]] += 1

                for alco in alco_mentioned:
                    self.major_alco_mentioned[alco_list_conversion.get(alco, alco)] += text.count(alco)

            if neos_used := [neo for neo in NEOLOGISMS if neo in text]:
                for neo in neos_used:
                    self.neologisms_mentioned[neo] += text.count(neo)

            message_date = parser.parse(message["date"])
            self.length_message[len(text)] += 1

            self.words_amount[len(text.split())] += 1

            hour = message_date.hour
            self.messages_per_hour[f"{hour}-{hour + 1}"] += 1

            if text.lower() == text:

                for sym in text:
                    self.symbol_amount[sym] += 1

                self.upper_lower_sym["lower case symbol"] += len(text)
                self.upper_lower["lower case message"] += 1

            elif text.upper() == text:

                for sym in text:
                    self.symbol_amount[sym] += 1

                self.upper_lower_sym["upper case symbol"] += len(text)
                self.upper_lower["upper case message"] += 1
            else:

                for sym in text:
                    self.symbol_amount[sym] += 1

                    upper_lower_sym_key = "upper case symbol" if sym.isupper() else "lower case symbol"
                    self.upper_lower_sym[upper_lower_sym_key] += 1

            punctuation_case_key = "with punctuation" \
                if any(s in punctuation for s in text) else "without punctuation"
            self.punctuation[punctuation_case_key] += 1

            try:
                lang = langdetect.detect(text)
                if lang in ["uk", "ru"]:
                    self.languages[lang] += 1

                    if message_date.date() < PUKIN_STARTED_WAR:
                        self.messages_by_lang_before_war[lang] += 1
                    else:
                        self.messages_by_lang_war[lang] += 1
            except Exception:
                pass
        else:
            super().handle(message)

    def response(self) -> None:
        for res in [
            (self.length_message, "message_length", "amount", "amount of messages based on their length"),
            (self.words_amount, "words in message", "amount", "amount of messages based on their words amount"),
            (self.messages_per_hour, "message hour", "amount", "amount of messages based on the hour of day", True),
        ]:
            draw_single_res(*res)

        for res in [
            (self.neologisms_mentioned, True, "neologism mentions by users"),
            (self.symbol_amount, True, "symbols by their amount"),
            (self.major_alcocholics, True, "alco mentions by users"),
            (self.major_alco_mentioned, True, "alco mentions by type"),
            (self.punctuation, True, "punctuation used"),
            (self.upper_lower_sym, True, "upper lower symbols used"),
            (self.upper_lower, True, "upper lower messages"),
            (self.languages, False, "languages used for all time"),
            (self.messages_by_lang_before_war, True, "Lang of messages before war"),
            (self.messages_by_lang_war, True, "Lang of messages during war"),
        ]:
            draw_circle_graph(*res)

        super().response()


class PhotoHandler(MessageHandler):
    def __init__(self):
        self.photos_per_hour = defaultdict(int)

    def handle(self, message: dict):
        if message["type"] == "photo":
            hour = int(re.search("\s[0-9]+", message["date"]).group(0).lstrip())
            self.photos_per_hour[f"{hour}-{hour + 1}"] += 1
        else:
            super().handle(message)

    def response(self):
        for res in [
            (
                self.photos_per_hour,
                "photo hour",
                "amount",
                "amount of photos based on the hour of day",
                True,
            ),
        ]:
            draw_single_res(*res)

        super().response()


class VideoHandler(MessageHandler):
    def __init__(self):
        self.length_video = defaultdict(int)
        self.videos_per_hour = defaultdict(int)

    def handle(self, message: dict):
        if message["type"] == "video":

            hour = int(re.search("\s[0-9]+", message["date"]).group(0).lstrip())
            self.videos_per_hour[f"{hour}-{hour + 1}"] += 1
            self.length_video[message["duration"]] += 1
        else:
            super().handle(message)

    def response(self):
        for res in [
            (
                self.length_video,
                "video duration",
                "amount",
                "amount of videos based on their duration",
                True,
            ),
            (
                self.videos_per_hour,
                "video hour",
                "amount",
                "amount of videos based on the hour of day",
                True,
            ),
        ]:
            draw_single_res(*res)

        super().response()
