import os
from metrica import *
from metrica_with_statictics import *
from excel import  *
import logging
import shutil

if __name__ == '__main__':
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    """else:
        shutil.rmtree(download_dir)
        os.makedirs(download_dir)"""
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.info('This will get logged')

    print('Выбери режим\n1. Для SEO\n'
          '2. Для рекламной статистики')
    choice = int(input())
    if choice == 1:
        parse_metrica()

        dir_list = os.listdir(work_dir)
        print(dir_list)
        for papka in dir_list:
            if not os.path.exists(papka + '.zip'):
                shutil.make_archive(papka, 'zip', work_dir + '//' + papka)
    if choice == 2:
        parse_stats()
        ex_work()