import os
import xlwt, xlrd
import xlsxwriter
from xlutils.copy import copy


def write_to_file(filename, msg, mode='w+'):
    with open(r"C:\Users\micha\PycharmProjects\Bubs\mpSpider\Pages\%s" % filename, mode, encoding='gb18030') as f:
        f.write(msg)
        f.close()


def read_from_file(filename):
    with open(r"C:\Users\micha\PycharmProjects\Bubs\mpSpider\Pages\%s" % filename, "r+", encoding='gb18030') as f:
        return f.read()


def save_to_excel(pItem, filename):
    fhead = r"C:\Users\micha\PycharmProjects\Bubs\mpSpider\{fname}"
    fname = fhead.format(fname=filename)

    if os.path.isfile(fname) == False:
        workbook = xlsxwriter.Workbook(fname)
        worksheet = workbook.add_worksheet('Bubs')
        titlefmt = workbook.add_format()
        titlefmt.set_font('Arial')
        titlefmt.set_bold()
        titlefmt.set_align('center')
        worksheet.set_row(0, 8, titlefmt)
        format = titlefmt
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 60)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)

        worksheet.write(0, 0, 'ProductId')
        worksheet.write(0, 1, 'ProductName')
        worksheet.write(0, 2, 'ProductPrice')
        worksheet.write(0, 3, 'SalesVolume')
        worksheet.write(0, 4, 'ShopName')
        worksheet.write(0, 5, 'URL')
        worksheet.write(0, 6, 'Source')
        worksheet.write(0, 7, 'Date')
        for idx, values in enumerate(pItem):
            worksheet.write(idx + 1, 0, values[0])
            worksheet.write(idx + 1, 1, values[1].strip('\t\n '))
            worksheet.write(idx + 1, 2, values[2])
            worksheet.write(idx + 1, 3, values[3])
            worksheet.write(idx + 1, 4, values[4])
            worksheet.write(idx + 1, 5, values[5])
            worksheet.write(idx + 1, 6, values[6])
            worksheet.write(idx + 1, 7, values[7])
        workbook.close()
    else:
        workbook = xlrd.open_workbook(fname)
        worksheet = workbook.sheet_by_name('Bubs')
        rows = worksheet.nrows
        previousData = copy(workbook)
        newsheet = previousData.get_sheet(0)
        for idx, values in enumerate(pItem.prdName):
            newsheet.write(rows + idx, 0, pItem.prdId[idx])
            newsheet.write(rows + idx, 1, values.strip('\t\n '))
            newsheet.write(rows + idx, 2, pItem.shopName[idx])
            newsheet.write(rows + idx, 3, float(pItem.prdPrice[idx]))
            newsheet.write(rows + idx, 4, int(pItem.prdSales[idx]))
            newsheet.write(rows + idx, 5, pItem.prdUrl[idx])
            newsheet.write(rows + idx, 6, pItem.source[idx])
            newsheet.write(rows + idx, 7, pItem.date)
        previousData.save(fname)