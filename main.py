from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import time
import io
import os
import logging
from PIL import Image


# Основной метод - настраивает браузер, логинится и узнает о сайтах во вкладке SEO
def parse_metrica():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # не отображает браузер вообще
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    login(driver)

    # находим список сайтов во вкладке SEO
    driver.find_element_by_xpath("//span[text()='SEO']").click()
    time.sleep(3)

    sites = driver.find_elements_by_class_name('counters-list-table-item')

    # и по каждому сайту выполняем процедуру сбора информации с дашборда и конверсий, возвращаемся на начальную страницу
    # со списком сайтов и заново создаем список, потому что после возвращения к начальной странице мы не сможем
    # обратиться к конкретному сайту из необновленного списка - каждый элемент страницы имеет обновляемый уникальный
    # айдишник поэтому нам досточно знать количество отслеживаемых сайтов и обращаться по-индексово к sites[]
    for i in range(0, len(sites)):
        # нахождение и клик по нужному сайту
        site = sites[i]
        page = site.find_element_by_class_name('counters-list-table-item__counter-info')
        page_name = page.find_element_by_class_name('link').text.replace(' ', '').replace('.', '')

        # заставляем спуститься к элементу, иначе словим исключение
        driver.execute_script("arguments[0].scrollIntoView(false);", page)
        page.find_element_by_class_name('link').click()

        # парсим дашборд с конверсией
        parser_of_dashboard(driver, page_name)

        # возврат к странице со списком SEO
        driver.get('https://metrika.yandex.ru/list')
        driver.find_element_by_xpath("//span[text()='SEO']").click()
        time.sleep(4)
        sites = driver.find_elements_by_class_name('counters-list-table-item')


# выполняет процедуру захода в кабинет
def login(driver):
    driver.get('https://metrika.yandex.ru/list')
    driver.implicitly_wait(10)  # ожидание по возможному безействию
    time.sleep(6)

    with open("data.json") as f:
        data = json.load(f)

        input = driver.find_element_by_class_name('Textinput-Control')
        input.send_keys(data['login'])
        driver.find_element_by_class_name('Button2_type_submit').click()
        time.sleep(1)
        input = driver.find_element_by_id('passp-field-passwd')
        input.send_keys(data['pass'])
        driver.find_element_by_class_name('Button2_type_submit').click()

        time.sleep(6)


def parser_of_dashboard(driver, watching='demo'):
    time.sleep(6)

    # создаем папку для сайта
    if not os.path.exists(watching):
        os.makedirs(watching)
    f = open(f"{watching}//{watching}.txt", "w", encoding='utf-8')

    # указываем что нужны данные в дашборде за месяц
    mouth = driver.find_element_by_xpath("//*[contains(text(),'Месяц')]/..")
    mouth.click()

    time.sleep(3)

    # находим графики,круговые диаграммы и численные виджеты
    graphical = driver.find_elements_by_class_name('widget_type_multiline')
    circles = driver.find_elements_by_class_name('widget.widget_type_pie')
    totals = driver.find_elements_by_class_name('widget_type_total')

    # проходится по виджетам с графиками - делает скриншот виджета и записывает текстовую информацию
    for elem in graphical:
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        zagolovok = elem.find_element_by_class_name('widget__title').text
        numbers = elem.find_element_by_class_name('chart-legend__value').text
        text = zagolovok + ' ' + numbers + '\n'
        f.write(text)
        time.sleep(1)
        capture_element(elem, zagolovok, watching)
        f.write('\n')

    # также с численными виджетами
    for elem in totals:
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        zagolovok = elem.find_element_by_class_name('widget__title').text
        numbers = elem.find_element_by_class_name('widget-preview__total').text
        text = zagolovok + ' ' + numbers + '\n'
        f.write(text)
        time.sleep(1)
        capture_element(elem, zagolovok, watching)
        f.write('\n')

    # проходится по кругововым диаграммам - делаеи скриншот, захолит на страницу диаграммы
    # и записывает её части с названием части, значением и процентом в файл
    for i in range(0, len(circles)):
        elem = driver.find_elements_by_class_name('widget.widget_type_pie')[i]
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        time.sleep(2)

        zagolovok = elem.find_element_by_class_name('smart-link')
        f.write(zagolovok.text + '\n')
        capture_element(elem, zagolovok.text, watching)

        # идем на страницу круговой диаграммы
        zagolovok.click()

        time.sleep(5)

        # ищем строки с инфой
        table = driver.find_element_by_class_name('data-table__tbody')
        driver.execute_script("arguments[0].scrollIntoView(false);", table)
        rows = table.find_elements_by_xpath("child::node()")

        data = {}

        # защита от кнопки "показать ещё"
        button_show_more = rows[len(rows) - 1]
        if 'Показать ' in button_show_more.text:
            rows.remove(button_show_more)

        # собираем название с фатическими значениями
        for row in rows:
            ActionChains(driver).move_to_element(row)
            site = row.find_element_by_class_name('data-table__dimension-description').text
            elem = row.find_element_by_class_name('data-table__cell_type_metric')
            numbers = elem.find_element_by_class_name('data-table__metricym-s-visits_type_absolute').text
            data[site] = numbers

        driver.find_element_by_class_name('data-table__head-button_action_percent').click()

        # а теперь отдельно и проценты
        for row in rows:
            ActionChains(driver).move_to_element(row)
            site = row.find_element_by_class_name('data-table__dimension-description').text
            percents = row.find_element_by_class_name('data-table__metricym-s-visits_type_relative').text
            data[site] += f' ({percents})'

        # записываем в файл
        for key, value in data.items():
            f.write(key + ' ' + value + '\n')
        driver.back()
        time.sleep(3)

        f.write('\n')

    # ищем виджеты с таблицами
    tables = driver.find_elements_by_class_name('widget_type_table')

    for i in range(0, len(tables)):
        # обычно виджет с поисковыми запросами всегда последний для него процедура такая же как с диаграммами
        # с остальными просто делаем скриншоты
        if i != len(tables) - 1:
            elem = tables[i]
            driver.execute_script("arguments[0].scrollIntoView(false);", elem)
            zagolovok = elem.find_element_by_class_name('widget-title__inner').text
            data = elem.find_element_by_class_name('widget__stats').text
            time.sleep(1)
            capture_element(elem, zagolovok, watching)
            container = data
            f.write(container)
            f.write('\n\n')
        else:
            # для поисковых запросов
            elem = tables[i]
            driver.execute_script("arguments[0].scrollIntoView(false);", elem)
            zagolovok = elem.find_element_by_class_name('widget-title__inner')
            f.write(zagolovok.text + '\n')
            zagolovok.click()
            time.sleep(5)
            # есть сайты у которых не набираются поисковые запросы в количестве > 50 - кнопки "показать ещё" не будет
            # поэтому защищаемся от исключения
            try:
                button = driver.find_element_by_class_name('show-more__button')
                driver.execute_script("arguments[0].scrollIntoView(false);", button)
                time.sleep(2)
                button.click()
                time.sleep(2)
            except Exception as e:
                logging.warning(
                    f'На {watching} не найдена кнопка увеличения количества поисковых запросов, беру то что есть',
                    exc_info=True)
                pass

            # вытаскиваю запрос с его количеством и записываю в файл
            rows = driver.find_elements_by_class_name('data-table__row')
            for row in rows:
                driver.execute_script("arguments[0].scrollIntoView(false);", row)
                f.write(row.text.replace('\n', ' ') + '\n')
            time.sleep(2)

            # вытаскивание показателей конверсий
            conversion_finder(driver, watching)

    f.close()


def conversion_finder(driver, watching: str):
    # ищем кнопку с Отчетами и кликаем
    menu_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "main-menu__item_type_reports")))
    menu_button.click()
    # заставляем мышь провести над кнопкой со стандартными отчетами
    conversion_button = driver.find_element_by_class_name('main-menu-finder__item_id_standart-reports')
    ActionChains(driver).move_to_element(conversion_button).perform()
    # генерится менюшка и нажимаем на кнопку конверсий
    driver.find_element_by_class_name('main-menu-finder__item_key_conversion-rate').click()

    # собираем все цели, спускаемся по каждой цели и делаем скриншот
    time.sleep(5)
    reports = driver.find_elements_by_class_name('conversion-report__goal')
    for report in reports:
        driver.execute_script("arguments[0].scrollIntoView(false);", report)
        name = report.find_element_by_class_name('conversion-report__goal-title-text').text
        capture_element(report, name, watching)


# сохранение скриншота элемента сайта
def capture_element(element, uniq, directory):
    image = element.screenshot_as_png
    imagestream = io.BytesIO(image)
    im = Image.open(imagestream)
    # убираем все мешающие для сохранения файла символы
    im.save(directory + '//' + uniq.replace(' ', '_').replace(':', '').replace('"', '')
            .replace('//', '').replace('\n', '') + '.png')


if __name__ == '__main__':
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.info('This will get logged')
    parse_metrica()
# login()
