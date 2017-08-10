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
    fhead = r"C:\Users\micha\PycharmProjects\Bubs\mpSpider\Data\{fname}"
    fname = fhead.format(fname=filename)

    workbook = xlsxwriter.Workbook(fname)
    worksheet = workbook.add_worksheet('Bubs')
    titlefmt = workbook.add_format()
    titlefmt.set_font('Arial')
    titlefmt.set_bold()
    titlefmt.set_align('center')
    worksheet.set_row(0, 15, titlefmt)
    cellfmt = workbook.add_format({'font':'Arial'})
    cellfmt.set_font_size(9)
    cellfmt.set_align('left')
    worksheet.set_column('A:H', 10, cellfmt)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 66)

    headings = ['Date', 'Source', 'Shop Name', 'Product Name', 'Sales Volume', 'Price', 'Id', 'URL']
    worksheet.write_row('A1', headings)

    for idx, values in enumerate(pItem):
        worksheet.write(idx + 1, 0, values[7])
        worksheet.write(idx + 1, 1, values[6])
        worksheet.write(idx + 1, 2, values[4])
        worksheet.write(idx + 1, 3, values[1].strip('\t\n ')) # prod name
        worksheet.write(idx + 1, 4, values[3])
        worksheet.write(idx + 1, 5, values[2])
        worksheet.write(idx + 1, 6, values[0])
        worksheet.write(idx + 1, 7, values[5])
    workbook.close()