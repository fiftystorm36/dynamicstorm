import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from statistics import mean
from tqdm import tqdm
import multiprocessing as mp

from . import model as dymod
from . import statistics as dyst


class Filter:
    """誤ベクトル数の確認，誤ベクトル数によるフィルタリング処理"""

    @classmethod
    def show_incorrect_vector_example(cls, file_list, example_number):
        """含まれる瞬時データの内100個がそれぞれ持つ誤ベクトル数を表示する"""
        incorrect_vector_list = []
        try:
            file_list = file_list[0:example_number]
        except:
            pass
        for i, file in enumerate(tqdm(file_list)):
            total_incorrect_vector = cls.get_total_incorrect_vector(file)
            incorrect_vector_list.append(total_incorrect_vector)
        incorrect_vector_mean = mean(incorrect_vector_list)

        # plot
        plt.title('incorrect vector NO. of first {} data'.format(example_number))
        plt.scatter(range(len(incorrect_vector_list)), incorrect_vector_list)
        plt.axhline(incorrect_vector_mean, color='black')
        plt.text(0, incorrect_vector_mean + 50, 'mean value = ' + str(incorrect_vector_mean))
        plt.gca().yaxis.set_minor_locator(tick.MultipleLocator(100))
        plt.grid(which='minor')
        plt.show()

    def show_incorrect_vector_all(self, file_list):
        """含まれる瞬時データ全てがそれぞれ持つ誤ベクトル数を表示する"""
        incorrect_vector_list = []
        for i, file in enumerate(tqdm(file_list)):
            total_incorrect_vector = cls.get_total_incorrect_vector(file)
            incorrect_vector_list.append(total_incorrect_vector)
        incorrect_vector_mean = mean(incorrect_vector_list)

        # plot
        plt.title('incorrect vector NO. of all data')
        plt.scatter(range(len(incorrect_vector_list)), incorrect_vector_list)
        plt.axhline(incorrect_vector_mean, color='black')
        plt.text(0, incorrect_vector_mean + 50, 'mean value = ' + str(incorrect_vector_mean))
        plt.grid()
        plt.show()

    @staticmethod
    def filter_incorrect_vector(file_list, filter_value):
        """ファイル名のリストから，誤ベクトル数がfilter_value以上のファイルの名前を除外する"""
        before = len(file_list)
        print('Processing')
        totalcore = mp.cpu_count()
        pool = mp.Pool(totalcore)
        args = [(file_list, totalcore, i, filter_value) for i in range(totalcore)]
        callback = pool.map(parallel_task, args)
        error_index_list = []
        for each_error_index_list in callback:
            for error_index in each_error_index_list:
                error_index_list.append(error_index)
        error_index_list.sort(reverse=True)
        for error_index in error_index_list:
            del file_list[error_index]
        after = len(file_list)
        print('finish!\n''filtered file:', str(before - after) + '/' + str(before))
        return file_list

    @staticmethod
    def get_total_incorrect_vector(file):
        """瞬時データに含まれる誤ベクトルの数を返す"""
        data = dymod.InstantData(file)
        status = data.get_data('Status')
        return np.sum((status == 1) | (status == 17))


def parallel_task(args):
    """並列計算タスク"""
    file_list, totalcore, currentcore, filter_value = args
    file_count = len(file_list)
    start = int(file_count * currentcore / totalcore)
    end = int(file_count * (currentcore + 1) / totalcore) - 1
    header = dymod.InstantData.get_header_row(file_list[0])
    error_file_index_list = []
    if currentcore == 0:
        text = 'task ' + '1/' + str(totalcore)
        for i in tqdm(range(start, end), desc=text):
            status = pd.read_csv(file_list[i], header=header)['Status']
            if np.sum((status == 1) | (status == 17)) >= filter_value:
                error_file_index_list.append(i)
        print('Wait till other {} parallel tasks will have finished.'.format(totalcore - 1))
    else:
        for i in range(start, end):
            status = pd.read_csv(file_list[i], header=header)['Status']
            if np.sum((status == 1) | (status == 17)) >= filter_value:
                error_file_index_list.append(i)
    return error_file_index_list
