import os

print(os.getcwd())
#os.chdir('../../mounts')
#print(os.getcwd())
file = '../../mounts/files/in/2024.csv'

EXP_HEADERS = 'Category,Name,Desciption,Kids,Judge'
categories = []
with open(file, encoding='utf-8-sig') as fh:
    for c, line in enumerate(x.rstrip() for x in fh):
        cells = line.split(',')
        if c == 0: # header
            init_headers = ','.join(cells[0:5])
            if init_headers != EXP_HEADERS:
                raise Exception(f'Failed to import {file}, incorrect header, expected {EXP_HEADERS},*')
        else:
            item = {
                    'Category': cells[0],
                    'Name': cells[1],
                    'Desciption': cells[2],
                    'Kids': cells[3],
                    'Judge': cells[4],
                    'Cups': list(x for x in cells[5:] if x)
                    }
            print(item)

