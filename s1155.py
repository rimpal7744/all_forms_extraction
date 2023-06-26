import json
import os

import pytesseract
import PyPDF2
import pdfplumber
import camelot
import re
import io
from pdf2image import convert_from_path
import numpy as np
from collections import Counter
def get_key_boxes(result):
    # match regex for all key values from OCR result and get their boxes
    boxes = []
    # to append names given in forms for key values
    names = []
    keys_name = []
    # rating=''
    contract, requisition, Date, order = False, False, False, False
    for element in result:
        # all regex matching for keys respectively

        # Contract_regexp = re.compile(r'(PURCH)|(CONTRACT)|(CONIRACT)|(Contract)')
        Contract_regexp = re.compile(r'(contract)|(coniract)')
        # Contract_regexp2 = re.compile(r'(ORDER)|(NO)|(NO.)|(NUMBER)|(no.)|(No.)')
        Contract_regexp2 = re.compile(r'(purch)')
        Date_regexp = re.compile(r'(date)')
        Date_regexp2 = re.compile(r'(order)')
        Priority_regexp = re.compile(r'(priority)|(dpas15)')
        Requisition_regexp = re.compile(r'(req/purch)|(purch.request)|(requisition)|(purchase)')
        Requisition_regexp2 = re.compile(r'(number)|(no.)|(no)')
        Order_regexp = re.compile(r'(delivery)')
        Order_regexp2 = re.compile(r'(order)|(no.)')
        Issued_regexp = re.compile(r'(issued)')
        Issued_regexp2 = re.compile(r'(by)')
        Admin_regexp = re.compile(r'(administered)(admnistered)|(admnistered)')
        Admin_regexp2 = re.compile(r'(by)')
        Account_regexp = re.compile(r'(accounting)|(appropriation)')
        Account_regexp2 = re.compile(r'(data)')
        sentence = element[1][0].replace(' ', '').lower()
        if Contract_regexp.search(sentence) and Contract_regexp2.search(sentence):
            # if Contract_regexp.search(sentence) and Contract_regexp2.search(sentence):
            if contract == False:
                contract = True
                # if (('2') in element[1][0]) or (('2.') in element[1][0]):
                names.append(element[1][0])
                keys_name.append('purchase_number')
                boxes.append([element[0], 'purchase_number'])
        if Order_regexp.search(sentence) and Order_regexp2.search(sentence):
            if order == False:
                order = True
                new_value = element[0]
                if element[1][0] in names:
                    element_index = names.index(element[1][0])
                    value = boxes[element_index][0][0][0]
                    element_name = boxes[element_index][1]
                    if element_name == 'purchase_number':
                        new_value = [[float(value) + 240, boxes[element_index][0][0][1]], [0, 0], [0, 0], [0, 0]]

                names.append(element[1][0])
                keys_name.append('delivery_number')
                boxes.append([new_value, 'delivery_number'])
        if Date_regexp.search(sentence) and Date_regexp2.search(sentence):
            if Date == False:
                Date = True
                new_value = element[0]

                if element[1][0] in names:
                    element_index = names.index(element[1][0])
                    value = boxes[element_index][0][0][0]

                    element_name = boxes[element_index][1]
                    if element_name == 'purchase_number':
                        new_value = [[value * 2, boxes[element_index][0][0][1]], [0, 0], [0, 0], [0, 0]]
                    if element_name == 'delivery_number':
                        new_value = [[float(value) + 200, boxes[element_index][0][0][1]], [0, 0], [0, 0], [0, 0]]

                names.append(element[1][0])
                keys_name.append('effective_date')
                boxes.append([new_value, 'effective_date'])
        if Requisition_regexp.search(sentence) and Requisition_regexp2.search(sentence):
            if requisition == False:
                requisition = True
                new_value = element[0]

                if element[1][0] in names:
                    element_index = names.index(element[1][0])
                    element_name = boxes[element_index][1]
                    value = boxes[element_index][0][0][0]
                    value2 = boxes[element_index][0][0][1]
                    if element_name == 'delivery_number':
                        new_value = [[value * 2, boxes[element_index][0][0][1]], [0, 0], [0, 0], [0, 0]]
                    if element_name == 'effective_date':
                        new_value = [[float(value) + 200, boxes[element_index][0][0][1]], [0, 0], [0, 0], [0, 0]]

                names.append(element[1][0])
                keys_name.append('requisition_number')
                boxes.append([new_value, 'requisition_number'])

        if Priority_regexp.search(sentence) and len(sentence) < 18:
            names.append(element[1][0])
            keys_name.append('priority')
            boxes.append([element[0], 'priority'])

        if Issued_regexp.search(sentence) and Issued_regexp2.search(sentence):
            names.append(element[1][0])
            keys_name.append('issued_by')
            boxes.append([element[0], 'issued_by'])
        if Admin_regexp.search(sentence) and Admin_regexp2.search(sentence):
            names.append(element[1][0])
            keys_name.append('administered_by')
            boxes.append([element[0], 'administered_by'])
        if Account_regexp.search(sentence) and Account_regexp2.search(sentence):
            names.append(element[1][0])
            boxes.append([element[0], 'accounting_data'])
    # returning boxes list having coordinates of all key values with their name like given below list
    # [[[651.0, 133.0], [815.0, 133.0], [815.0, 156.0], [651.0, 156.0]],effective_date]

    return boxes, names, keys_name


def get_first_page(result):
    my_dict = {'purchase_number': '', 'effective_date': '', 'requisition_number': '', 'delivery_number': '',
               'issued_by': '', 'administered_by': '', 'standard_form': '', 'priority': '', 'accounting_data': ''}

    boxes, names, keys = get_key_boxes(result)

    if ('administered_by' not in keys) and ('issued_by' in keys):
        issue_box = float(boxes[keys.index('issued_by')][0][1][0])
        new_coordinates = [[[issue_box * 3.5, boxes[keys.index('issued_by')][0][0][1]], [0, 0], [0, 0], [0, 0]],
                           'administered_by']
        boxes.append(new_coordinates)
    if 'delivery_number' in keys and 'effective_date' not in keys:
        delivery_box = float(boxes[keys.index('delivery_number')][0][1][0])
        new_coordinates = [
            [[delivery_box + 100, boxes[keys.index('delivery_number')][0][0][1]], [0, 0], [0, 0], [0, 0]],
            'effective_date']
        boxes.append(new_coordinates)
    issued_text = []
    admin_text = []
    issuedx_coordinate = ''
    issuedy_coordinate = ''
    adminx_coordinate = ''
    adminy_coordinate = ''
    issue_code = ''
    admin_code = ''
    admin_value = ''
    contractor = False
    for r in result:
        form1155regexp = re.compile(r'(FORM 1155)|(FORM1155)|(Form 1155)')
        #  saving a form type
        if form1155regexp.search(str(r[1][0])):
            # if 'FORM'  or 'Form' in str(r[1][0]):
            my_dict['standard_form'] = str(r[1][0])

        if r[1][0].replace(' ', '').lower() == 'seeitem6' and 850 > r[0][0][0] > 650 and 450 > r[0][0][1] > 300:
            admin_value = r[1][0]

        for i in boxes:
            # algo for getting CODE value in adminstered by
            if admin_code == '':
                if i[1] == 'administered_by':
                    Adminregexp = re.compile(r'(ADMINISTERED)')
                    Adminregexp2 = re.compile(r'(BY)|(8Y)')
                    if Adminregexp.search(r[1][0]) and Adminregexp2.search(r[1][0]):
                        present = result.index(r)
                        admin_string = result[present + 2][1][0]
                        digit = 0
                        for ch in admin_string:
                            if ch.isdigit():
                                digit = digit + 1
                        if digit >= 3 or len(admin_string.split(' ')) == 1:
                            admin_code = 'Code: ' + result[present + 2][1][0].replace('|', '')

            # algo for getting CODE value in ISSUED by
            if issue_code == '':
                if i[1] == 'issued_by':
                    Issuedregexp = re.compile(r'(ISSUED)')
                    Issuedregexp2 = re.compile(r'(BY)|(8Y)')
                    if Issuedregexp.search(r[1][0]) and Issuedregexp2.search(r[1][0]):
                        present = result.index(r)
                        splited = result[present + 1][1][0].split(' ')
                        splited_2 = result[present + 2][1][0].split(' ')
                        if len(splited) == 2:
                            if splited[0] == 'CODE':
                                issue_code = "CODE: " + splited[1].replace('|', '')
                            elif splited[0] == 'Code':
                                issue_code = "CODE: " + splited[1].replace('|', '')
                        if issue_code == '':
                            if len(splited_2) == 2:
                                if splited_2[0] == 'CODE':
                                    issue_code = "CODE: " + splited_2[1].replace('|', '')
                                elif splited[0] == 'Code':
                                    issue_code = "CODE: " + splited_2[1].replace('|', '')
                        if issue_code == '':
                            issued_string = result[present + 2][1][0]
                            digit = 0
                            for ch in issued_string:
                                if ch.isdigit():
                                    digit = digit + 1
                            if digit >= 3 or len(issued_string.split(' ')) == 1:
                                issued_string = issued_string.replace('|', '')
                                issue_code = 'CODE: ' + issued_string

            # defining different x and y coordinates for different keys
            if str(i[1]) == 'requisition_number':
                x_coordinate = 301
                y_coordinate = 150
            elif str(i[1]) == 'administered_by':
                x_coordinate = 150
                y_coordinate = 100
            elif str(i[1]) == 'accounting_data':
                x_coordinate = 700
                y_coordinate = 150
            elif str(i[1]) == 'priority':
                x_coordinate = 700
                y_coordinate = 120
            else:
                x_coordinate = 100
                y_coordinate = 120

            # checking value which matches algo on coordinates
            if (-10 <= (r[0][0][1] - i[0][0][1]) < y_coordinate) and -20 <= (r[0][0][0] - i[0][0][0]) < x_coordinate and \
                    r[1][0] not in names:
                value = r[1][0].replace('|', '')

                if i[1] != 'issued_by' and i[1] != 'administered_by':
                    # getting values below the key value boxes and save them to json
                    if i[1] == 'effective_date':
                        value = value.replace('Mby', 'May')
                        value = value.replace('I', '1')

                    if my_dict[i[1]] == '':
                        if str(i[1]) == 'priority':
                            if ('8.' in value) or ('destination' in value.lower()) or (value.lower() == 'do'):
                                value = ''
                        if ('AGREEMENTNO' not in value) and ('yyyy' not in value.lower()):
                            my_dict[i[1]] = value
                # issued_by and adminstered by have large values so combining all values to issued_text and admin_text
                if i[1] == 'issued_by':
                    issuedx_coordinate = r[0][0][0]
                    issuedy_coordinate = r[0][0][1]
                    if issue_code not in issued_text:
                        issued_text.append(issue_code)
                if i[1] == 'administered_by':
                    adminx_coordinate = r[0][0][0]
                    adminy_coordinate = r[0][0][1]
                    if admin_code not in admin_text:
                        admin_text.append(admin_code)

        if adminy_coordinate:
            if -15 <= (r[0][0][0] - adminx_coordinate) < 10 and 0 <= (r[0][0][1] - adminy_coordinate) <= 85:
                if r[1][0] not in admin_text:
                    admin_text.append(r[1][0])
                adminx_coordinate = r[0][0][0]
                adminy_coordinate = r[0][0][1]
        if issuedx_coordinate:
            if -15 <= (r[0][0][0] - issuedx_coordinate) < 15 and 0 <= (r[0][0][1] - issuedy_coordinate) <= 80:
                if 'CONTRACTOR' in r[1][0] or '9.' in r[1][0]:
                    contractor = True
                if contractor == False:
                    if r[1][0] not in issued_text:
                        issued_text.append(r[1][0])
                    issuedx_coordinate = r[0][0][0]
                    issuedy_coordinate = r[0][0][1]

    # joining issued_text and administered_text to feed in json
    if len(issued_text) > 0:
        my_dict['issued_by'] = '\n'.join(issued_text)
    if len(admin_text) > 0:
        my_dict['administered_by'] = '\n'.join(admin_text)
    if my_dict['standard_form'] == '':
        my_dict['standard_form'] = 'STANDARD FORM 1155'
    if my_dict['delivery_number'] == my_dict['purchase_number']:
        my_dict['delivery_number'] = ''
    if my_dict['administered_by'] == '' and admin_value != '':
        my_dict['administered_by'] = admin_value

    return my_dict


def get_tables_pages(pdf_path):
    method = ''
    with pdfplumber.open(pdf_path) as pdf:
        # Get number of pages
        NumPages = len(pdf.pages)
        String = "ITEM NO"
        String2 = "QUANTITY UNIT"
        String3 = "ITEM"
        String4 = "Total Item Amount"
        String5 = "SUPPLIES OR SERVICES "
        table_pagess = []
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search(String, Text) and re.search(String2, Text):
                method = 'first'
                table_pagess.append(i)
            if re.search(String3, Text) and re.search(String4, Text) and re.search(String5, Text):
                method = 'second'
                table_pagess.append(i)
        if len(table_pagess) > 0:
            if method == 'first' or method == 'second':
                table_pagess.append(table_pagess[-1] + 1)

    return table_pagess


def get_tables_method(pdf_path, pages):

    all_pages = ','.join(str(v) for v in pages)
    items = []
    try:
        tables = camelot.read_pdf(pdf_path, flavor='stream', edge_tol=500, pages=str(all_pages))

        for table in tables:
            try:
                df = table.df
                cols = len(df.axes[1])

                method_first = False
                third_method = False
                if cols == 2:
                    df.columns = ['item', 'supplies_or_services']
                    # df.columns = ['item', 'supplies_or_services', 'quantity', 'unit', 'unit_price', 'amount']
                    method_first = True
                elif cols == 3:
                    df.columns = ['item', 'supplies_or_services1', 'supplies_or_services2']
                    df['supplies_or_services'] = df['supplies_or_services1'] + df['supplies_or_services2']
                    df["quantity"] = ""
                    df["unit"] = ""
                    df["unit_price"] = ""
                    df["amount"] = ""
                    method_first = True
                elif cols == 6:
                    df.columns = ['item', 'supplies_or_services', 'quantity', 'unit', 'unit_price', 'amount']
                    item_no_index = df.loc[df['item'] == 'ITEM NO'].index
                    if len(item_no_index) > 0:
                        third_method = True
                    else:
                        df.columns = ['item', 's1', 's2', 's3', 's4', 's5']
                        df['supplies_or_services'] = df['s1'] + df['s2'] + ['s3'] + ['s4'] + ['s5']
                        df["quantity"] = ""
                        df["unit"] = ""
                        df["unit_price"] = ""
                        df["amount"] = ""
                        method_first = True
                elif cols == 5:
                    df.columns = ['item', 'supplies_or_services', 'quantity', 'unit', 'amount']
                    df['unit_price'] = ''
                    item_no_index = df.loc[df['item'] == 'ITEM NO'].index
                    if len(item_no_index) > 0:
                        third_method = True
                elif cols == 7:
                    df.columns = ['item', 's1', 's2', 's3', 's4', 's5', 's6']
                    df["digit_value"] = df["item"].str.isdigit()

                if method_first == True:
                    indexxx = df.loc[df['item'] == 'ITEM'].index
                    df = df[df.item != 'CPIF  Services']
                    df = df.reset_index()
                    target_df = df.iloc[(indexxx[0] + 1):, ]
                    new_index_list = target_df.loc[target_df['item'] != ''].index
                    new_index_list = new_index_list.tolist()
                    for index_x in new_index_list:
                        next = new_index_list.index(index_x) + 1
                        if index_x != new_index_list[-1]:
                            final_target_df = df.iloc[index_x:new_index_list[next]]
                        if index_x == new_index_list[-1]:
                            final_target_df = df.iloc[index_x:]
                        supplies_or_services_list = final_target_df["supplies_or_services"].tolist()
                        first_index = supplies_or_services_list[1].split(' ')
                        amount = ''
                        for amount_checking in first_index:
                            if '$' in amount_checking or 'NSP' in amount_checking:
                                amount = amount_checking

                        if amount != '':
                            supplies_or_services_text = ' '.join(supplies_or_services_list[2:])
                        elif amount == '':
                            for text in supplies_or_services_list:
                                amount_text = text.split(' ')[-1]
                                if amount_text == ' ':
                                    amount_text = text.split(' ')[-2]
                                if '$' in amount_text:
                                    amount = amount_text
                            supplies_or_services_text = ' '.join(supplies_or_services_list)
                        my_dict = {}
                        my_dict['item'] = final_target_df.iloc[0]['item']
                        my_dict['supplies_or_services'] = supplies_or_services_text
                        my_dict['quantity'] = ''
                        my_dict['unit'] = ''
                        my_dict['unit_price'] = ''
                        my_dict['amount'] = amount
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(supplies_or_services_text)
                        my_dict['clauses'] = array
                        items.append(my_dict)

                elif method_first == False and third_method == True:
                    count = 0
                    for i in item_no_index:
                        target_df = df.iloc[i + 1]
                        json1 = target_df.to_json()
                        aDict = json.loads(json1)
                        if item_no_index[-1] == i:
                            full_text = []
                            new_target = df.iloc[(i + 1):]
                            for index, row in new_target.iterrows():
                                full_text.append(row['supplies_or_services'])
                                full_text.append('\n')
                                full_text.append(row['quantity'])
                                full_text.append('\n')
                            str1 = ''.join(full_text)
                            aDict['supplies_or_services'] = str1
                            name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                            array = name.findall(str1)
                            aDict['clauses'] = array
                            items.append(aDict)
                            count += 1
                        else:
                            full_text = []
                            new_target = df.iloc[i + 1:item_no_index[count + 1] - 1]
                            for index, row in new_target.iterrows():
                                full_text.append(row['supplies_or_services'])
                                full_text.append('\n')
                                full_text.append(row['quantity'])
                                full_text.append('\n')
                            str1 = ''.join(full_text)
                            count += 1
                            name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                            array = name.findall(str1)
                            aDict['supplies_or_services'] = str1
                            aDict['clauses'] = array
                            items.append(aDict)

                elif method_first == False:

                    digits_index = df.loc[df["digit_value"] == True].index
                    digits_index_list = digits_index.tolist()
                    for index_x in digits_index_list:
                        if index_x != digits_index_list[-1]:
                            next = digits_index_list[digits_index_list.index(index_x) + 1]
                            final_target_df = df.iloc[index_x:next]
                            data_target_df = df.iloc[index_x + 1:next]
                        if index_x == digits_index_list[-1]:
                            final_target_df = df.iloc[index_x:]
                            data_target_df = df.iloc[index_x + 1:]

                        full_text = []
                        amount = ''
                        for index, row in data_target_df.iterrows():
                            full_text.append(row['item'])
                            full_text.append(' ')
                            full_text.append(row['s1'])
                            full_text.append(' ')
                            full_text.append(row['s2'])
                            full_text.append(' ')
                            full_text.append(row['s3'])
                            full_text.append(' ')
                            full_text.append(row['s4'])
                            full_text.append(' ')

                            full_text.append(row['s5'])
                            full_text.append(' ')
                            full_text.append(row['s6'])
                            full_text.append(' ')
                            if '$' in (row['s5'].split(' ')[-1]) or ('NSP' in row['s5'].split(' ')[-1]):
                                amount = row['s5'].split(' ')[-1]
                            elif ('$' in row['s6'].split(' ')[-1]) or ('NSP' in row['s6'].split(' ')[-1]):
                                amount = row['s6'].split(' ')[-1]


                        supplies_or_services_text = ' '.join(full_text)
                        my_dict = {}
                        my_dict['item'] = final_target_df.iloc[0]['item']
                        my_dict['supplies_or_services'] = supplies_or_services_text
                        my_dict['quantity'] = ''
                        my_dict['unit'] = ''
                        my_dict['unit_price'] = ''
                        amount = re.sub(r'\s*[A-Za-z$]+\b', '', amount)
                        my_dict['amount'] = amount
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(supplies_or_services_text)
                        my_dict['clauses'] = array
                        items.append(my_dict)

            except Exception as e:
                pass

    except Exception as e:
        pass

    for item_dict in items:
        supplies_text=item_dict['supplies_or_services']
        supplies_text = os.linesep.join([s for s in supplies_text.splitlines() if s])
        item_dict['supplies_or_services']=supplies_text.replace('\n',' ')
        item_dict['amount'] = re.sub(r'\s*[A-Za-z$]+\b', '', item_dict['amount'])

    return items


def checking_clause_value(splited_clause):
    value_list = []
    try:
        if (splited_clause[0]==splited_clause[0].upper()) and (splited_clause[1]==splited_clause[1].upper()):
            for clause_value in splited_clause:
                if clause_value.upper() == clause_value:
                    value_list.append(clause_value)
                else:
                    break
        else:
            for clause_value in splited_clause:
                value_list.append(clause_value)
    except:
        for clause_value in splited_clause:
            value_list.append(clause_value)

    return value_list

def get_clauses(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        clauses_list = []
        Months_list = ['random_x', 'jan', 'feb', 'mar', "apr", 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        Months_list2 = ['random_x', 'jan', 'feb', 'mar', "apr", 'may', 'june', 'july', 'aug', 'sept', 'oct', 'nov', 'dec']

        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            Text = Text.replace('DFARS', '')
            Text = Text.replace('FAR', '')
            Text = Text.replace('DLAD', '')
            #matching clauses pattern to get relevant line
            NumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = NumRegex.search(Text)
            array_length = NumRegex.findall(Text)
            #after matching pattern applied multiple conditions to extract clauses
            try:
                if array.group():

                    NumRegex2 = re.compile(r'\d{4}', flags=0)
                    NumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    lines = Text.split('\n')
                    for line in lines:
                        actual_line = line
                        if line[0]==' ':
                            line=line[1:]
                        line=line.strip()
                        splited_line = line.split(' ')
                        try:
                            next_line = lines[lines.index(line) + 1]
                            splited_next_line = next_line.strip().split(' ')
                        except:
                            pass
                        try:
                            third_line = lines[lines.index(next_line) + 1]
                            splited_third_line = third_line.strip().split(' ')
                        except:
                            pass
                        try:
                            fourth_line = lines[lines.index(next_line) + 2]
                            splited_fourth_line = fourth_line.strip().split(' ')
                        except:
                            pass
                        if len(line)>20:
                            if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_next_line[-1]):
                                if not NumRegex2.search(splited_line[-1]):
                                    line = line + ' ' + next_line
                                    if len(line) > 20:
                                        line = line.strip()
                                        line = line.replace('(', '')
                                        line = line.replace(')', '')
                                        new_split_line = line.split(' ')
                                        months_text=new_split_line[-2].lower()
                                        if months_text in Months_list:
                                            new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(months_text))
                                            new_split_line = new_split_line[:-1]
                                            line = ' '.join(new_split_line)
                                        if '/' in new_split_line[-1]:
                                            month = new_split_line[-1].split('/')[0]
                                            year = new_split_line[-1].split('/')[2]
                                            new_split_line[-1] = year + '-' + month
                                            line = ' '.join(new_split_line)
                                        clauses_list.append(line)
                                        pass

                            if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_third_line[-1]):
                                if (not NumRegex2.search(splited_line[-1])) and (not NumRegex2.search(splited_next_line[-1])):
                                    line = line + ' ' + next_line +' '+third_line
                                    if len(line) > 20:
                                        line = line.strip()
                                        line = line.replace('(', '')
                                        line = line.replace(')', '')
                                        new_split_line = line.split(' ')
                                        months_text = new_split_line[-2].lower()
                                        if months_text in Months_list:
                                            new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(months_text))
                                            new_split_line = new_split_line[:-1]
                                            line = ' '.join(new_split_line)
                                        elif months_text in Months_list2:
                                            new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list2.index(months_text))
                                            new_split_line = new_split_line[:-1]
                                            line = ' '.join(new_split_line)
                                        if '/' in new_split_line[-1]:
                                            month = new_split_line[-1].split('/')[0]
                                            year = new_split_line[-1].split('/')[2]
                                            new_split_line[-1] = year + '-' + month
                                            line = ' '.join(new_split_line)
                                        clauses_list.append(line)
                                        pass

                            elif NumRegex.search(splited_line[0]) and NumRegex2.search(splited_fourth_line[-1]):
                                if len(splited_line)>2:
                                    statement=(not NumRegex2.search(splited_line[-1])) and (not NumRegex2.search(splited_next_line[-1])) and (not NumRegex2.search(splited_third_line[-1]))
                                else:
                                    statement= (not NumRegex2.search(splited_next_line[-1])) and (not NumRegex2.search(splited_third_line[-1]))
                                if  statement:
                                    line = line + ' ' + next_line +' '+third_line+ ' '+fourth_line
                                    if len(line) > 20:
                                        line = line.strip()
                                        line = line.replace('(', '')
                                        line = line.replace(')', '')
                                        new_split_line = line.split(' ')
                                        months_text = new_split_line[-2].lower()
                                        if months_text in Months_list:
                                            new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(months_text))
                                            new_split_line = new_split_line[:-1]
                                            line = ' '.join(new_split_line)
                                        elif months_text in Months_list2:
                                            new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list2.index(months_text))
                                            new_split_line = new_split_line[:-1]
                                            line = ' '.join(new_split_line)
                                        if '/' in new_split_line[-1]:
                                            month = new_split_line[-1].split('/')[0]
                                            year = new_split_line[-1].split('/')[1]
                                            new_split_line[-1] = year + '-' + month
                                            line = ' '.join(new_split_line)
                                        clauses_list.append(line)
                                        pass

                            if NumRegex.search(splited_line[0]) and (NumRegex2.search(splited_line[-1])):
                                second_string = False
                                try:
                                    next_string = lines[lines.index(actual_line) + 1]
                                    next_string_split = next_string.split(' ')
                                    if len(line) >= 50 and len(array_length) > 3:
                                        try:
                                            if (not NumRegex.search(next_string_split[0])) and (not NumRegex.search(next_string_split[1])):
                                                second_string=True
                                        except:
                                            if (not NumRegex.search(next_string_split[0])):
                                                second_string = True
                                except:
                                    pass
                                if len(line) > 20:
                                    line = line.replace('(', '')
                                    line = line.replace(')', '')
                                    line=line.strip()
                                    new_split_line = line.split(' ')
                                    months_text = new_split_line[-2].lower()
                                    if months_text in Months_list:
                                        new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(months_text))
                                        new_split_line = new_split_line[:-1]
                                        line = ' '.join(new_split_line)

                                    elif months_text in Months_list2:
                                        new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list2.index(months_text))
                                        new_split_line = new_split_line[:-1]
                                        line = ' '.join(new_split_line)
                                    if '/' in new_split_line[-1]:
                                        month = new_split_line[-1].split('/')[0]
                                        year = new_split_line[-1].split('/')[2]
                                        new_split_line[-1] = year + '-' + month
                                        line = ' '.join(new_split_line)
                                    if second_string==True:
                                        line=line.split(' ')
                                        line=' '.join(line[0:-1])+' '+next_string+' '+line[-1]
                                    clauses_list.append(line)
                                    pass

                            if NumRegex.search(splited_line[0]) and (NumRegex3.search(splited_line[-1])):
                                if len(line.split(' ')) == 2:

                                    line = splited_line[0] + ' ' + lines[lines.index(line) - 1] + ' ' + lines[lines.index(line) + 1] + ' ' + splited_line[-1]
                                    clauses_list.append(line)
                        if len(line)<20:
                            if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_next_line[-1]):
                                line = line + ' ' + next_line
                            elif NumRegex.search(splited_line[0]) and  NumRegex2.search(splited_third_line[-1]):
                                if (not NumRegex2.search(splited_next_line[-1])) and (not NumRegex.search(splited_next_line[0])) :
                                    line = line + ' ' + next_line+' '+third_line
                            if len(line) > 20:
                                line = line.strip()
                                line = line.replace('(', '')
                                line = line.replace(')', '')
                                new_split_line = line.split(' ')
                                months_text = new_split_line[-2].lower()
                                if months_text in Months_list:
                                    new_split_line[-2] = new_split_line[-1] + '-' + str(
                                        Months_list.index(months_text))
                                    new_split_line = new_split_line[:-1]
                                    line = ' '.join(new_split_line)
                                if '/' in new_split_line[-1]:
                                    month = new_split_line[-1].split('/')[0]
                                    year = new_split_line[-1].split('/')[2]
                                    new_split_line[-1] = year + '-' + month
                                    line = ' '.join(new_split_line)
                                clauses_list.append(line)

            except Exception as e:
                pass

    #changing clauses format
    clauses_new_list = []
    for clauses in clauses_list:
        splited_clause = clauses.split(' ')
        if (splited_clause[-1][0:3]).lower() in Months_list:
            splited_clause[-1]=splited_clause[-1][3:]+'-'+str(Months_list.index((splited_clause[-1][0:3]).lower()))
        if (splited_clause[-1][0:3]).lower() in Months_list2:
            splited_clause[-1]=splited_clause[-1][3:]+'-'+str(Months_list2.index((splited_clause[-1][0:3]).lower()))
        if len(splited_clause[-1].split('-'))==2 and '.' not in splited_clause[-1] :
            alpharemoval = re.sub(r'\s*[A-Za-z]+\b', '', splited_clause[-1])
            splited_clause[-1] = alpharemoval.rstrip()
            value_list=checking_clause_value(splited_clause[1:-1])
            updated_value_new=' '.join(value_list)
            if 'SECTION F - DELIVERIES' in updated_value_new:
                updated_value_new=updated_value_new.split('SECTION F - DELIVERIES')[0]
            updated_clause = splited_clause[0] + ' | ' + updated_value_new + ' | ' + splited_clause[-1]
            clauses_new_list.append(updated_clause)

    if len(clauses_new_list)>2:
        clauses_new_list=list(set(clauses_new_list))

    return clauses_new_list






def mains1155(pdf_path,result):
    # for getting data from first_page
    my_dict=get_first_page(result)
    #for getting numbers of pages which have line_items
    page_number_list=get_tables_pages(pdf_path)
    #for getting line_items from table_pages
    if len(page_number_list)>1:
        line_items=get_tables_method(pdf_path,page_number_list)
    else:
        line_items=[]
    my_dict['items']=line_items
    my_dict['clauses']=get_clauses(pdf_path)
    #for returning response
    return my_dict
