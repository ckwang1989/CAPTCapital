import pandas as pd

def to_excel(outputs, excel_p='result.xlsx'):
    '''
        input:
            outputs: [{'k1': v1, 'k2': v2....}, {'k1': v1, 'k2': v2....} ...]
        output:
            excel_file
    '''
    df = pd.DataFrame(outputs)
    df.to_excel(excel_p)