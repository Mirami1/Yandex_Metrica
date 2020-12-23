from PIL import Image
import io
import time
import re
import json
# сохранение скриншота элемента сайта
def capture_element(element, uniq, directory, category):
    image = element.screenshot_as_png
    imagestream = io.BytesIO(image)
    im = Image.open(imagestream)
    # убираем все мешающие для сохранения файла символы
    uniq = re.sub('[:"/]', '', uniq)
    im.save(directory + '//' + category + '//' + uniq.replace('\n', ' ') + '.png')

# выполняет процедуру захода в кабинет
def login_metrica(driver):
    driver.get('https://metrika.yandex.ru/list')
    driver.implicitly_wait(10)  # ожидание по возможному безействию
    time.sleep(6)

    with open("data.json") as f:
        data = json.load(f)

        input = driver.find_element_by_class_name('Textinput-Control')
        input.send_keys(data['metrica']['login'])
        driver.find_element_by_class_name('Button2_type_submit').click()
        time.sleep(1)
        input = driver.find_element_by_id('passp-field-passwd')
        input.send_keys(data['metrica']['pass'])
        driver.find_element_by_class_name('Button2_type_submit').click()

        time.sleep(6)

def login_stats(driver):
    driver.get('https://metrika.yandex.ru/list')
    driver.implicitly_wait(10)  # ожидание по возможному безействию
    time.sleep(6)

    with open("data.json") as f:
        data = json.load(f)

        input = driver.find_element_by_class_name('Textinput-Control')
        input.send_keys(data['stats']['login'])
        driver.find_element_by_class_name('Button2_type_submit').click()
        time.sleep(1)
        input = driver.find_element_by_id('passp-field-passwd')
        input.send_keys(data['stats']['pass'])
        driver.find_element_by_class_name('Button2_type_submit').click()

        time.sleep(6)