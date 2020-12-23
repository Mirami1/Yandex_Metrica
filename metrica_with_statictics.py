from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv
from utils import *
import os

work_dir = 'Results'
download_dir = 'Download'


def parse_stats():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # не отображает браузер вообще
    prefs = {'download.default_directory': os.path.abspath(download_dir),
             "download.prompt_for_download": False,
             "download.directory_upgrade": True,
             "safebrowsing_for_trusted_sources_enabled": False,
             "safebrowsing.enabled": False}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    # чтобы каждая строка с конверсией была нормального размера, иначе скринит обрезанно в ширину
    driver.set_window_size(1920, 1080)
    login_stats(driver)

    time.sleep(3)

    sites = driver.find_elements_by_class_name('counters-list-table-item')

    sites_name = [i.find_element_by_class_name('link').text for i in sites]

    print('Общие показатели и поведенческие факторы')
    print('Выбери из списка нужные сайты под цифрой через пробел:')
    for i in range(0, len(sites_name)):
        print(str((i + 1)) + '. ' + sites_name[i])

    numbers = list(map(int, input('\nВаш выбор : ').strip().split()))

    for i in range(0, len(numbers)):
        # нахождение и клик по нужному сайту
        site = sites[numbers[i] - 1]
        page = site.find_element_by_class_name('counters-list-table-item__counter-info')
        page_name = page.find_element_by_class_name('link').text.replace('\n', '').replace('.', '')

        # заставляем спуститься к элементу, иначе словим исключение
        driver.execute_script("arguments[0].scrollIntoView(false);", page)
        page.find_element_by_class_name('link').click()
        get_stats(driver, page_name)

        driver.get('https://metrika.yandex.ru/list')
        time.sleep(4)
        sites = driver.find_elements_by_class_name('counters-list-table-item')
    driver.get('https://direct.yandex.ru/registered/main.pl?stat_type=campdate&ulogin=kosdirectim&cmd=showCampStat')
    time.sleep(10)
    driver.find_element_by_xpath("//*[text()='30 дней']").click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[@role='listbox']").click()
    time.sleep(1)
    popup_list = driver.find_elements_by_class_name('select__item')
    popup_list[2].click()
    driver.find_element_by_class_name('b-statistics-form__submit-button').click()
    time.sleep(15)
    driver.find_element_by_class_name('b-statistics-form__download').click()
    time.sleep(10)


def get_stats(driver, page_name):
    time.sleep(6)

    # ищем кнопку с Отчетами и кликаем

    menu_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "main-menu__item_type_reports")))
    menu_button.click()
    # заставляем мышь провести над кнопкой со стандартными отчетами
    conversion_button = driver.find_element_by_class_name('main-menu-finder__item_id_standart-reports')
    ActionChains(driver).move_to_element(conversion_button).perform()
    # генерится менюшка и нажимаем на кнопку конверсий
    driver.find_element_by_class_name('main-menu-finder__item_key_traffic').click()

    # собираем все цели, спускаемся по каждой цели и делаем скриншот
    time.sleep(3)
    # reports = driver.find_elements_by_class_name('conversion-report__goal')

    print('\nСайт ' + page_name)

    print("Введи промежуток отслеживания в формате 15.01.2020  01.02.2020 или нажми пробел, "
          "чтобы промежуток отслеживания был месяцем")

    gap = input()
    if gap.strip() == '':
        mouth = driver.find_element_by_xpath("//*[contains(text(),'Месяц')]/..")
        mouth.click()
    else:
        begin, end = gap.strip().split()
        driver.find_element_by_class_name('date-range-selector__selector-button').click()
        driver.find_element_by_class_name('super-calendar__from').click()
        driver.find_element_by_class_name('super-calendar__from').clear()
        driver.find_element_by_class_name('super-calendar__from').send_keys(begin)
        driver.find_element_by_class_name('super-calendar__to').click()
        driver.find_element_by_class_name('super-calendar__to').clear()
        driver.find_element_by_class_name('super-calendar__to').send_keys(end)
        driver.find_element_by_class_name('super-calendar__show').click()
    buttons2 = driver.find_elements_by_class_name('add-filter-button__button')
    buttons2[1].click()

    container = driver.find_element_by_class_name('add-filter-button__popup-content')
    container.find_element_by_class_name('sources').click()
    sourse = driver.find_element_by_class_name('sources')
    sourse.find_element_by_class_name('sources_last').click()
    driver.find_element_by_class_name('advEngine').click()
    time.sleep(6)

    checkboxes = driver.find_elements_by_class_name('segment-panel-checkbox-list__item')
    for checkbox in checkboxes:
        checkbox.click()
        time.sleep(1)

    driver.find_element_by_class_name('segment-panel__confirm').click()
    table = driver.find_element_by_class_name('data-table__thead')
    names = table.find_elements_by_class_name('data-table__thead-row')[1]
    names = names.find_elements_by_class_name('data-table__cell')[1:]

    name = [i.text.replace('\n', "") for i in names]
    info = driver.find_element_by_class_name('data-table__totals-row')
    driver.execute_script("arguments[0].scrollIntoView(false);", info)
    time.sleep(2)
    info = driver.find_element_by_class_name('data-table__totals-row')
    info = info.find_elements_by_class_name('data-table__cell')[1:]
    numbers = [i.text.replace('\u2009', "") for i in info]
    numb_in_dict = dict(zip(name, numbers))
    file = open(f"{page_name+' Посещаемость'}.csv", mode='w', encoding='utf-16', newline='')
    with file:
        writer = csv.DictWriter(file, fieldnames=name, dialect='excel-tab')
        writer.writeheader()
        writer.writerow(numb_in_dict)
    time.sleep(5)
