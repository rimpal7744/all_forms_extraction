import json
import os

import pandas as pd
import tabula
import re
import pdfplumber
import camelot

def get_key_boxes(result):
    #match regex for all key values from OCR result and get their boxes
    boxes=[]
    #to append names given in forms for key values
    names=[]
    actual_names=[]
    for element in result:
        #all regex matching for keys respectively
        Contract_regexp = re.compile(r'(CONTRACT)|(CONIRACT)|(CONTRACI)|(CONTRA CT)')
        Contract_regexp2 = re.compile(r'(NO)|(NO.)|(NUMBER)')
        Date_regexp = re.compile(r'(DAIE)|(DATE)')
        Date_regexp2 = re.compile(r'(ISSUED)')
        Rating_regexp = re.compile(r'(RATING)|(RAIING)')
        Email_regexp = re.compile(r'(E-MAIL ADDRESS)|(E-MAILADDRESS)')
        Email_regexp2 = re.compile(r'(C)|(C.)')
        Requisition_regexp = re.compile(r'(REQUISITION)|(RE QUISITION)|(SOLICITAIION)')
        Requisition_regexp2 = re.compile(r'(NUMBER)|(NO.)|(NO)')
        Solicitation_regexp = re.compile(r'(SOLICITATION)|(SOLICITAIION)')
        Solicitation_regexp2 = re.compile(r'(NO)|(NUMBER)|(NO.)')
        Solicitation_type_regexp = re.compile(r'(SOLICITATION)')
        Solicitation_type_regexp2 = re.compile(r'(TYPE)')
        Amendmentno_regexp = re.compile(r'(AMENDMENT)')
        Amendmentno_regexp2 = re.compile(r'(NO)|(NUMBER)')
        Award_amount_regexp = re.compile(r'(AMOUNT)')
        Award_amount_regexp2 = re.compile(r'(20)')
        Award_date_regexp = re.compile(r'(AWARDDAIE)|(AWARDDATE)|(AWARD DATE)')
        Award_date_regexp2 = re.compile(r'(28)|(28.)')
        Offer_date_regexp = re.compile(r'(OFFERDATE)|(OFFERDAIE)|(OFFER DATE)')
        Offer_date_regexp2 = re.compile(r'(18)|(18.)')
        Area_code_regexp = re.compile(r'(AREA CODE)|(area_code)')
        Extension_regexp = re.compile(r'(EXTENSION)')
        Name_regexp = re.compile(r'(NAME)|(name)')
        Name_regexp2 = re.compile(r'(A.)|(A)')
        Name_regexp3 = re.compile(r'(FOR INFORMATION)')
        Telephone_regexp = re.compile(r'(B. TELEPHONE)|(B.TELEPHONE)')
        Telephone_regexp2 = re.compile(r'(Include)')
        number_regexp = re.compile(r'(INUMBER)')
        if Rating_regexp.search(element[1][0]) :
            if 'rating' not in actual_names:
                names.append(element[1][0])
                actual_names.append('rating')
                boxes.append([element[0], 'rating'])
        if Contract_regexp.search(element[1][0]) and Contract_regexp2.search(element[1][0]):
            if ('2') in element[1][0]:
                if 'contract_number' not in actual_names:
                    names.append(element[1][0])
                    actual_names.append('contract_number')
                    boxes.append([element[0], 'contract_number'])
        if Date_regexp.search(element[1][0]) and Date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'date_issued'])
        if Requisition_regexp.search(element[1][0]) and Requisition_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'requisition/purchase_number'])
        if Solicitation_regexp.search(element[1][0]) and Solicitation_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'solicitation_number'])
        if Solicitation_type_regexp.search(element[1][0]) and Solicitation_type_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'solicitation_type'])
        if Amendmentno_regexp.search(element[1][0]) and Amendmentno_regexp2.search(element[1][0]):
            if '14' not in element[1][0]:
                names.append(element[1][0])
                boxes.append([element[0], 'amendment_no'])
        if Award_date_regexp.search(element[1][0]) and Award_date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'award_date'])
        if Offer_date_regexp.search(element[1][0]) and Offer_date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'offer_date'])
        if Award_amount_regexp.search(element[1][0]) and Award_amount_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'award_amount'])
        if Email_regexp.search(element[1][0]) and Email_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'email'])
        if Name_regexp.search(element[1][0]) and Name_regexp2.search(element[1][0]):
            if 'name' not in actual_names:
                if not Name_regexp3.search(element[1][0]):
                    names.append(element[1][0])
                    actual_names.append('name')
                    boxes.append([element[0], 'first_name'])
                elif  Name_regexp3.search(element[1][0]):
                    names.append(element[1][0])
                    actual_names.append('name')
                    boxes.append([element[0], 'second_name'])
        if Area_code_regexp.search(element[1][0]):
            if 'area_code' not in actual_names:
                names.append(element[1][0])
                actual_names.append( 'area_code')
                boxes.append([element[0], 'area_code'])
        if number_regexp.search(element[1][0]):
            if 'number' not in actual_names:
                names.append(element[1][0])
                actual_names.append( 'number')
                boxes.append([element[0], 'number'])
        if Extension_regexp.search(element[1][0]):
            if 'extension' not in actual_names:
                names.append(element[1][0])
                actual_names.append('extension')
                boxes.append([element[0], 'extension'])
        if Telephone_regexp.search(element[1][0]) and Telephone_regexp2.search(element[1][0]):
            if 'full_number' not in actual_names:
                names.append(element[1][0])
                actual_names.append( 'full_number')
                boxes.append([element[0], 'full_number'])
        if element[1][0]=='DATE':
            names.append(element[1][0])
            boxes.append([element[0], 'date'])
    #returning boxes list having coordinates of all key values with their name like given below list
    # [[[651.0, 133.0], [815.0, 133.0], [815.0, 156.0], [651.0, 156.0]],effective_date]
    return boxes,names


def get_first_page(result):

    my_dict = {'contract_number': '', 'solicitation_number': '', 'solicitation_type': '', 'date_issued': '',
               'requisition/purchase_number': '', 'email': '', 'rating': '','name':'', 'area_code': '', 'extension': '',
               'number': '','amendment_no': [], 'date': [], 'award_date': '', 'award_amount': '', 'offer_date': '','full_number':''}

    boxes, names = get_key_boxes(result)
    amendments=[]
    dates_list=[]
    # iterating over a result from OCR and saving box which have value from all_keys
    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['standard_form']=str(line[1][0])

    for r in result:
        for i in boxes:
            if i[1]=='amendment_no':
                y=50
                x=50
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and -80 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    amendments.append(r[1][0])
                    my_dict[i[1]]=amendments
            elif i[1]=='date':
                x=50
                y=50
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and -30 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    dates_list.append(r[1][0])
                    my_dict[i[1]]=dates_list
            elif i[1]=='second_name':
                x=250
                y=40
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and 100 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    my_dict['name'] = r[1][0]
            elif i[1]=='full_number':
                x=80
                y=50
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and 0 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    my_dict['full_number'] = r[1][0]

            else:
                x=80
                y=80
                if (0<=(r[0][0][1]-i[0][0][1])<y) and -10<=(r[0][0][0]-i[0][0][0])<x and r[1][0] not in names :
                    value = r[1][0]
                    if i[1]=='first_name':
                        my_dict['name']=value
                    elif i[1]=='solicitation_type':
                        if "X" not in r[1][0]:
                            value='SEALED BID (IFB)'
                            my_dict[i[1]] = value
                        elif "X" in r[1][0]:
                            value='NEGOTIATED (RFP)'
                            my_dict[i[1]]=value
                    elif i[1]=='award_date':
                        value=r[1][0].replace('Mby','May')
                        my_dict[i[1]] = value

                    else:
                        # lists for classifying values for matching
                        my_dict[i[1]] = value

    if my_dict['full_number']!='':
        my_dict['number']=my_dict['full_number']
        my_dict.pop('full_number', None)
    elif my_dict['full_number']=='':
        my_dict.pop('full_number', None)
    if 'CALL' in my_dict['name']:
        my_dict['name']=''
    return my_dict


def get_tables_pages(pdf_path):
    method = ''
    with pdfplumber.open(pdf_path) as pdf:
        # Get number of pages
        NumPages = len(pdf.pages)
        String = "ITEM NO"
        String2="QUANTITY UNIT"
        String3="Item"
        String4="Unit Price"
        String5="Supplies/Service"
        string6="MAX UNIT"
        # Extract text and do the search for checking method and pages
        table_pagess=[]
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search(String,Text):
                if re.search(string6,Text):
                    method='third'
                    table_pagess.append(i)
            if re.search(String,Text):
                if re.search(String2,Text):
                    method='first'
                    table_pagess.append(i)
            if re.search(String3, Text) and re.search(String4, Text) and re.search(String5,Text):
                method='second'
                table_pagess.append(i)
        if len(table_pagess)>0 :
            if method=='first' or method=='third':
                table_pagess.append(table_pagess[-1]+1)

    return table_pagess,method


def first_method(pdf_path,pages):
    items = []
    current_page=pages[0]
    try:
        for page in pages:
            tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=500, pages=str(page))
            second_method=False
            itemno_list=[]

            for table in tables:
                try:
                    index_change=False
                    df = table.df
                    if len(df.columns) == 7:
                        df.columns = ['item', 'supplies_or_services', 'quantity', 'unit', 'unit_price', 'blank','amount']
                        df.drop('blank', axis=1, inplace=True)
                    elif len(df.columns)==4:
                        df.columns = ['item','supplies_or_services', 'quantity', 'unit']
                    elif len(df.columns)==6:
                        df.columns = ['item', 'supplies_or_services', 'quantity', 'unit', 'unit_price', 'amount']
                    elif len(df.columns)==5:
                        df.columns = ['item', 'supplies_or_services', 'quantity', 'unit', 'amount']
                        second_method=True
                    indexxx = df.loc[df['item'] == 'ITEM NO'].index
                    if len(indexxx) == 0:
                        indexxx = df.loc[df['item'] == 'ITEM NO \nSUPPLIES/SERVICES'].index
                        index_change = True
                    if len(indexxx) == 0:
                        if len(df.columns)==5 :
                            indexxx = df.loc[df['item'] == 'SUPPLIES/SERVICES'].index
                            if len(indexxx)!=0:
                                df.columns = ['supplies_or_services', 'quantity', 'unit','unit_price', 'amount']
                            df['item'] = ''
                            df.columns = ['supplies_or_services', 'quantity', 'unit', 'unit_price', 'amount','item']
                            first_column = df.pop('item')
                            df.insert(0, 'item', first_column)
                            index_change=False
                            second_method = False

                            with pdfplumber.open(pdf_path) as pdf:
                                Text = pdf.pages[current_page-1].extract_text()
                                splited_text=Text.split('PRICE AMOUNT\n')
                                for line in splited_text[1:]:
                                    if line.split(' ')[0] not in itemno_list:
                                        df['item'] = line.split(' ')[0]
                                        break

                        elif len(df.columns)==4:
                            indexxx = df.loc[df['item'] == 'SUPPLIES/SERVICES'].index
                            if len(indexxx)!=0:
                                df.columns = ['supplies_or_services', 'quantity', 'unit','unit_price']
                                df['amount']=df['unit_price']
                                df['item']=''
                                df.columns = ['supplies_or_services', 'quantity', 'unit', 'unit_price', 'amount', 'item']
                                first_column = df.pop('item')
                                df.insert(0, 'item', first_column)
                                index_change = False
                                second_method = False

                                with pdfplumber.open(pdf_path) as pdf:
                                    Text = pdf.pages[current_page-1].extract_text()
                                    splited_text = Text.split('PRICE AMOUNT\n')
                                    for line in splited_text[1:]:
                                        if line.split(' ')[0] not in itemno_list:
                                            df['item'] = line.split(' ')[0]
                                            break
                    count = 0
                    for i in indexxx:
                        dff = df.iloc[i + 1]

                        if second_method==True:
                            sss = dff['unit'].split('\n')
                            if len(sss) > 1:
                                dff['unit_price'] = sss[1]
                                dff['unit'] = sss[0]
                            else:
                                dff['unit_price'] = ''

                        if index_change == True:
                            data_change = [dff['supplies_or_services'], dff['quantity'], dff['unit']]
                            dff['quantity'] = data_change[0]
                            dff['unit'] = data_change[1]
                            dff['unit_price'] = data_change[2]
                        json1 = dff.to_json()
                        aDict = json.loads(json1)
                        if indexxx[-1] == i:
                            full_text = []
                            ccc = df.iloc[(i + 2):]
                            for index, row in ccc.iterrows():
                                full_text.append(row['supplies_or_services'])
                                full_text.append(row['quantity'])
                            str1 = ''.join(full_text)
                            name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                            array = name.findall(str1)
                            aDict['supplies_or_services'] = str1
                            aDict['clauses'] = array
                            itemno_list.append(aDict['item'])
                            items.append(aDict)
                            count += 1
                        else:
                            full_text = []
                            ccc = df.iloc[i + 2:indexxx[count + 1] - 1]
                            for index, row in ccc.iterrows():
                                full_text.append(row['supplies_or_services'])
                                full_text.append(row['quantity'])
                            str1 = ''.join(full_text)
                            name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                            array = name.findall(str1)
                            count += 1
                            aDict['supplies_or_services'] = str1
                            aDict['clauses'] = array
                            itemno_list.append(aDict['item'])
                            items.append(aDict)

                except:
                    pass
            current_page+=1
    except:
        pass
    for item_dict in items:
        supplies_text = item_dict['supplies_or_services']
        supplies_text = os.linesep.join([s for s in supplies_text.splitlines() if s])
        item_dict['supplies_or_services'] = supplies_text.replace('\n', ' ')
        item_dict['amount'] = re.sub(r'\s*[A-Za-z$]+\b', '', item_dict['amount'])

    return items


def method2(pdf_path,pages):
    items_list=[]
    for p in pages:
        page_end=p+10
        df = tabula.read_pdf(pdf_path, pages=str(p)+'-'+str(page_end),stream=True)
        tables_list = []
        tables = df
        count = 0
        data = []
        for table in tables:
            try:
                if count == 0:
                    value = table.columns
                    table.columns = value
                    supplies_value = table['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in supplies_value))
                    table.drop('Supplies/Service', axis=1, inplace=True)
                    table.dropna(axis=0, how='all', inplace=True)
                    count += 1
                    tables_list.append(table)
                else:
                    table.columns = value
                    supplies_value = table['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in supplies_value))
                    table.drop('Supplies/Service', axis=1, inplace=True)
                    table.dropna(axis=0, how='all', inplace=True)
                    tables_list.append(table)
            except:
                pass
    target_data= '.'.join(data)
    new_list = []
    target_data = target_data.replace('Firm Fixed Price', 'Firm Fixed Price fffff')
    target_data = target_data.replace('Cost No Fee', 'Cost No Fee fffff')
    target_data = target_data.split('fffff')
    line_clauses=[]
    for f in target_data:
        new_list.append(f)
        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
        array = name.findall(f)
        line_clauses.append(array)

    new_df = pd.concat(tables_list, axis=0, ignore_index=True)
    vv = new_df.loc[pd.isna(new_df["Item"]), :].index

    for v in vv:
        if pd.notnull(new_df['Unit Price'][v]):
            if pd.notnull(new_df['Unit Price'][v - 1]):
                new_df.iloc[v - 1, 3] = str(new_df.iloc[v - 1, 3]) + ' ' + str(new_df.iloc[v, 3])
            if pd.isnull(new_df['Unit Price'][v - 1]):
                new_df.iloc[v - 1, 3] = str(new_df.iloc[v, 3])
        if pd.notnull(new_df['Amount'][v]):
            if pd.notnull(new_df['Amount'][v + 1]):
                new_df.iloc[v + 1, 4] = str(new_df.iloc[v, 4]) + '\n' + str(new_df.iloc[v + 1, 4])
            elif pd.isnull(new_df['Amount'][v + 1]):
                new_df.iloc[v + 1, 4] = str(new_df.iloc[v, 4])

    new_df.dropna(thresh=2, axis=0, inplace=True)
    new_df['Supplies/Services'] = new_list
    new_df['Clauses'] = line_clauses
    items_json=new_df.to_json(orient="index")
    items_json=json.loads(items_json)

    for it in items_json:
        items_list.append(items_json[str(it)])
    for i in items_list:
        i['item'] = i['Item']
        del i['Item']
        i['quantity'] = i['Quantity']
        del i['Quantity']
        i['unit'] = i['Unit']
        del i['Unit']
        i['unit_price'] = i['Unit Price']
        del i['Unit Price']
        i['supplies_or_services'] = i['Supplies/Services']
        del i['Supplies/Services']
        i['Amount'] = re.sub(r'\s*[A-Za-z]+\b', '', str(i['Amount']))
        i['amount'] = i['Amount']
        del i['Amount']
        i['clauses'] = i['Clauses']
        del i['Clauses']
        item_value=str(int(i['item']))
        item_value_updated = item_value
        if len(item_value)==1:
            item_value_updated='000'+item_value
        elif len(item_value)==2:
            item_value_updated='00'+item_value
        elif len(item_value)==3:
            item_value_updated='0'+item_value
        i['item']=item_value_updated

    for item_dict in items_list:
        supplies_text = item_dict['supplies_or_services']
        supplies_text = os.linesep.join([s for s in supplies_text.splitlines() if s])
        item_dict['supplies_or_services'] = supplies_text.replace('\n', ' ')
        item_dict['amount'] = re.sub(r'\s*[A-Za-z$]+\b', '', item_dict['amount'])

    return items_list


def third_method(pdf_path,pages):
    all_pages=','.join(str(v) for v in pages)
    items = []
    try:
        tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=500, pages=all_pages)
        for table in tables:
            try:
                df = table.df
                df.columns = ['item', 'supplies_or_services', 'quantity', 'unit', 'unit_price', 'amount']

                indexxx = df.loc[df['item'] == 'ITEM NO'].index

                count = 0
                for i in indexxx:
                    target_df = df.iloc[i + 2]
                    json1 = target_df.to_json()
                    aDict = json.loads(json1)
                    if indexxx[-1] == i:
                        full_text = []
                        new_target = df.iloc[(i + 2):]
                        for index, row in new_target.iterrows():
                            full_text.append(row['supplies_or_services'])
                        str1 = ''.join(full_text)
                        aDict['supplies_or_services'] = str1
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        aDict['clauses'] = array
                        items.append(aDict)
                        count += 1
                    else:
                        full_text = []
                        new_target = df.iloc[i + 2:indexxx[count + 1] - 1]
                        for index, row in new_target.iterrows():
                            full_text.append(row['supplies_or_services'])
                        str1 = ''.join(full_text)
                        count += 1
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        aDict['supplies_or_services'] = str1
                        aDict['clauses'] = array
                        items.append(aDict)
            except:
                pass

    except:
        pass
    for item_dict in items:
        supplies_text = item_dict['supplies_or_services']
        supplies_text = os.linesep.join([s for s in supplies_text.splitlines() if s])
        item_dict['supplies_or_services'] = supplies_text.replace('\n', ' ')
        item_dict['amount'] = re.sub(r'\s*[A-Za-z$]+\b', '', item_dict['amount'])
    return items

def get_clauses(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        #get number of pages
        NumPages = len(pdf.pages)
        clauses_list=[]
        #list of all months to match
        # Months_list=['ggg','JAN','FEB','MAR',"APR",'MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        Months_list=['ggg','jan','feb','mar',"apr",'may','jun','jul','aug','sep','oct','nov','dec']
        Months_list2=['ggg','jan','feb','mar',"apr",'may','june','july','aug','sept','oct','nov','dec']
        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            NumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = NumRegex.search(Text)
            lenarray = NumRegex.findall(Text)
            #if pattern match then implementing various algos
            try:
                if array.group():
                    NumRegex2 = re.compile(r'\d{4}', flags=0)
                    NumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    splited_text = Text.split('\n')
                    for line in splited_text:
                        third = False
                        splited_line = line.split(' ')
                        try:
                            next_line = splited_text[splited_text.index(line) + 1]
                            next_line_splited=next_line.split(' ')
                        except:
                            pass
                        full_line=''
                        if NumRegex.search(splited_line[0]) and NumRegex2.search(next_line_splited[-1]):
                            if not NumRegex2.search(splited_line[-1]):
                                full_line = line + ' ' + next_line
                                if len(full_line) > 20:
                                    full_line = full_line.replace('(', '')
                                    full_line = full_line.replace(')', '')
                                    full_line_split = full_line.split(' ')
                                    if full_line_split[-2].lower() in Months_list:
                                        full_line_split[-2] = full_line_split[-1] + '-' + str(Months_list.index(full_line_split[-2].lower()))
                                        full_line_split = full_line_split[:-1]
                                        line = ' '.join(full_line_split)
                                    elif full_line_split[-2].lower() in Months_list2:
                                        full_line_split[-2] = full_line_split[-1] + '-' + str(Months_list2.index(full_line_split[-2].lower()))
                                        full_line_split = full_line_split[:-1]
                                        line = ' '.join(full_line_split)
                                    elif (full_line_split[-3] + full_line_split[-2]).lower() in Months_list:
                                        full_line_split[-2] = full_line_split[-1] + '-' + str(
                                            Months_list.index((full_line_split[-3] + full_line_split[-2]).lower()))
                                        full_line_split = full_line_split[:-1]
                                        line = ' '.join(full_line_split)
                                    if '/' in full_line_split[-1]:
                                        month = full_line_split[-1].split('/')[1]
                                        year = full_line_split[-1].split('/')[2]
                                        full_line_split[-1] = year + '-' + month
                                        line = ' '.join(full_line_split)
                                    clauses_list.append(line)


                        if NumRegex.search(splited_line[0]) and (NumRegex2.search(splited_line[-1])) :
                            length = False
                            try:
                                next_index=splited_text[splited_text.index(line)+1]

                                nexxx=next_index.split(' ')

                                if len(line)>=65 and len(lenarray)>3:
                                    if not NumRegex.search(nexxx[0]):
                                        length=True
                                        if line!=splited_text[-1] or line!=splited_text[-2] :
                                            thirddd=splited_text[splited_text.index(line) + 2]
                                            third_index = splited_text[splited_text.index(line) + 2].split(' ')
                                            if not NumRegex.search(third_index[0]) and len(third_index[0])<70 and len(lenarray)>8:
                                                third=True
                            except:
                                pass
                            if len(line)>20:
                                line=line.replace('(','')
                                line=line.replace(')','')
                                full_line_split=line.split(' ')
                                if full_line_split[-2].lower() in Months_list:
                                    full_line_split[-2]=full_line_split[-1]+'-'+str(Months_list.index(full_line_split[-2].lower()))
                                    full_line_split=full_line_split[:-1]
                                    line=' '.join(full_line_split)
                                elif full_line_split[-2].lower() in Months_list2:
                                    full_line_split[-2] = full_line_split[-1] + '-' + str(
                                        Months_list2.index(full_line_split[-2].lower()))
                                    full_line_split = full_line_split[:-1]
                                    line = ' '.join(full_line_split)
                                elif (full_line_split[-3]+full_line_split[-2]).lower() in Months_list:
                                    full_line_split[-2] = full_line_split[-1] + '-' + str(
                                        Months_list.index((full_line_split[-3]+full_line_split[-2]).lower()))
                                    full_line_split = full_line_split[:-1]
                                    line = ' '.join(full_line_split)

                                elif '-' in full_line_split[-2]:
                                    for i in Months_list:
                                        if i in full_line_split[-2].lower():
                                            full_line_split[-1] = full_line_split[-1] + '-' + str(
                                                Months_list.index(i))
                                            # full_line_split = full_line_split
                                            line = ' '.join(full_line_split)
                                if '/' in full_line_split[-1]:
                                    month=full_line_split[-1].split('/')[1]
                                    year=full_line_split[-1].split('/')[2]
                                    full_line_split[-1]=year+'-'+month
                                    line=' '.join(full_line_split)
                                if length==True and third==False:
                                    line=line.split(' ')
                                    line=' '.join(line[0:-1])+' '+next_index+' '+line[-1]
                                elif length==True and third==True:
                                    line = line.split(' ')
                                    line = ' '.join(line[0:-1]) + ' ' + next_index +' '+thirddd+ ' ' + line[-1]
                                clauses_list.append(line)

                        if NumRegex.search(splited_line[0]) and (NumRegex3.search(splited_line[-1])):
                            if len(line.split(' '))==2:
                                new_clause=splited_line[0]+' '+splited_text[splited_text.index(line)-1]+' '+splited_text[splited_text.index(line)+1]+' '+splited_line[-1]
                                clauses_list.append(new_clause)
            except Exception as e:
                pass

    clauses_new_list = []
    for c in clauses_list:
        splited_clause = c.split(' ')
        updated_clause = splited_clause[0] + ' | ' + ' '.join(splited_clause[1:-1]) + ' | ' + splited_clause[-1]
        clauses_new_list.append(updated_clause)
    return clauses_new_list




def main(pdf_path,result):

    #getting_data_from_first_page
    mydict=get_first_page(result)

    #getting method and page numbers
    pagess,method=get_tables_pages(pdf_path)

    #different methods to get lineitems depend on method
    if method=='first':
        iteemms=first_method(pdf_path,pagess)
        mydict['items']=iteemms
    elif method=='second':
        iteemms=method2(pdf_path,pagess)
        mydict['items'] = iteemms
    elif method=='third':
        iteemms=third_method(pdf_path,pagess)
        mydict['items']=iteemms
    elif method=='':
        mydict['items']=[]
    #for getting clauses
    clausess=get_clauses(pdf_path)
    mydict['clauses']=clausess
    return mydict

