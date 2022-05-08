import matplotlib.pyplot as plt
from itertools import islice


def chunks(data, size):
    it = iter(data)
    data_len = len(data)
    exact = data_len // size
    rest = data_len % size if data_len > size else 0
    slices = [*([exact] * size)]
    slices = slices if not rest else slices + [rest]

    if not slices[0]:
        slices = [1 for _ in range(data_len)]

    for slicer in slices:
        yield {k: data[k] for k in islice(it, slicer)}


def prepare_sort_dict(res_dict: dict) -> dict:
    sorted_dict: dict = dict(sorted(res_dict.items(), key=lambda item: item[0]))
    to_be_drawn = {}

    for split_dict in chunks(sorted_dict, 10):
        names = list(split_dict.keys())
        x_label_name = f"<{names[-1]}" if names[0] != names[-1] else names[0]
        names_result = sum(split_dict.values())
        to_be_drawn[x_label_name] = names_result

    return to_be_drawn


class DrawGraph:
    def __init__(self, left: list, height: list, tick_label: list, x_label: str, y_label: str, title: str):
        self.left = left
        self.height = height
        self.tick_label = tick_label
        self.x_label = x_label
        self.y_label = y_label
        self.title = title

    def draw(self):
        plt.rc("font", size=8)
        plt.bar(self.left, self.height, tick_label=self.tick_label, width=0.4, color=["red", "green"])
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title)
        plt.show()


def slice_dict(res_dict: dict) -> dict:
    res_dict = list(res_dict.items())[:1]
    res_dict = dict(res_dict)

    return res_dict


def draw_single_res(res_dict: dict, x_label: str, y_label: str, title: str, is_prepared: bool = False):
    to_be_drawn = prepare_sort_dict(res_dict=res_dict) if not is_prepared else res_dict
    to_be_drawn = slice_dict(to_be_drawn)

    graphic = DrawGraph(
        left=list(range(1, len(to_be_drawn) + 1)),
        height=list(to_be_drawn.values()),
        tick_label=list(to_be_drawn.keys()),
        x_label=x_label,
        y_label=y_label,
        title=title,
    )
    graphic.draw()


def draw_circle_graph(res_dict: dict, with_label=True, title=""):
    labels = list(res_dict.keys())
    sizes = list(res_dict.values())
    explode = [0.1 for _ in labels[:25]]
    fig1, ax1 = plt.subplots()

    if with_label:
        ax1.pie(sizes[:25], labels=labels[:25], startangle=90, explode=explode)
    else:
        ax1.pie(sizes[:25], startangle=90, explode=explode)

    ax1.axis('equal')
    plt.legend(labels)
    plt.title(title)
    plt.show()
