import os
# from tasks import AnyMessageHandler, TextHandler, VoiceHandler, PhotoHandler, VideoHandler
import csv
import argparse


class CSVWorker:
    def __init__(self, path: str, amount: int = None):
        self.path = path if path[-1] == "/" else f"{path}/"
        self.dialogs = [f"{self.path}{f}" for f in os.listdir(path) if f.endswith(".csv")]

        if amount:
            self.dialogs = self.dialogs[:amount]

    def launch_analysis(self):
        initial_handler = AnyMessageHandler()
        text_handler = TextHandler()
        voice_handler = VoiceHandler()
        photo_handler = PhotoHandler()
        video_handler = VideoHandler()
        initial_handler.set_next(text_handler)
        text_handler.set_next(voice_handler)
        voice_handler.set_next(photo_handler)
        photo_handler.set_next(video_handler)

        for dialog in self.dialogs:
            with open(dialog, mode="r") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    initial_handler.handle(message=row)

        initial_handler.response()


def launch_chain(handler):
    csv_worker = CSVWorker("dialogs", 20)

    for dialog in csv_worker.dialogs:
        with open(dialog, mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                handler.handle(message=row)

    handler.response()


if __name__ == "__main__":
    csv_worker = CSVWorker("dialogs", 20)
    parser = argparse.ArgumentParser(description='Enter amount of dialogs to be analysed')
    parser.add_argument("--dialog_amount", help="Slice of chosen amount of dialogs", default=None)
    args = parser.parse_args()
    csv_worker.launch_analysis()
