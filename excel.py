import xlwt, xlrd, glob

download_dir = 'Download'


def ex_work():
    get_dir = glob.glob(download_dir + '/*.xls')
    rb = xlrd.open_workbook(get_dir[0], formatting_info=True)

    sheet = rb.sheet_by_index(0)

    val = sheet.row_values(0)[0]

    vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]

    info = vals[0:5]

    numbers = vals[5:len(vals) - 1]

    numbers = [[0 if x == '-' else x for x in group] for group in numbers]

    sum_companies = []

    i = 0
    k = 0
    try:
        while i != len(numbers) - 1:
            if numbers[i][0] == numbers[i + 1][0]:
                print('sov')
                sum_companies.append([numbers[i][0], numbers[i][1], numbers[i][2] + '-' + numbers[i + 1][2]])
                for j in range(3, len(numbers[i])):
                    sum_companies[k].append(numbers[i][j] + numbers[i + 1][j])
                i += 2
                k += 1
            else:
                sum_companies.append([d for d in numbers[i]])
                i += 1
                k += 1
    except Exception as e:
        pass
    results = info + sum_companies + vals[-2:]

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Статистика по компаниям', cell_overwrite_ok=True)
    i = 0
    write_data(vals, ws)
    ws = wb.add_sheet('Итоги', cell_overwrite_ok=True)
    write_data(results, ws)



    wb.save(get_dir[0].replace(download_dir + '//', ""))
    pass


def write_data(data, ws):
    for i in range(0, len(data)):
        for j in range(len(data[i])):
            ws.write(i, j, data[i][j],
                     xlwt.easyxf("align: horiz center"))
