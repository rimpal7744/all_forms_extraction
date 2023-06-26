import json
import os

import pdfplumber
import camelot
import re

def get_key_boxes(result):
    #match regex for all key values from OCR result and get their boxes
    boxes=[]
    #to append names given in forms for key values
    names=[]
    rating=''
    for element in result:
        #all regex matching for keys respectively

        Contract_regexp = re.compile(r'(CONTRACT)|(CONIRACT)|(Contract)')
        Contract_regexp2 = re.compile(r'(NO)|(NO.)|(NUMBER)|(no.)|(No.)')
        Date_regexp = re.compile(r'(EFFECTIVE)|(EFFECIVE)|(Effective)')
        Date_regexp2 = re.compile(r'(DATE)|(DAIE)|(Date)')
        Rating_regexp = re.compile(r'(RATING)|(RAIING)|(Rating)')
        Requisition_regexp = re.compile(r'(PURCHASE)|(REQUISITION)|(Requisition)|(Purchase)')
        Requisition_regexp2 = re.compile(r'(NO)|(NUMBER)|(NO.)|(No.)')
        Project_regexp = re.compile(r'(PROJECT)|(Project)')
        Project_regexp2 = re.compile(r'(NO)|(NUMBER)')
        Issued_regexp = re.compile(r'(ISSUED)|(Issued)')
        Issued_regexp2 = re.compile(r'(BY)|(8Y)|(By)')
        Admin_regexp = re.compile(r'(ADMINISTERED)|(Administered)')
        Admin_regexp2 = re.compile(r'(BY)|(8Y)|(By)')
        if Rating_regexp.search(element[1][0]) :
                names.append(element[1][0])
                if len(element[1][0].lower().split('rating'))>1:
                    rating=element[1][0].lower().split('rating')[1]

                boxes.append([element[0], 'rating'])
        if Contract_regexp.search(element[1][0]) and Contract_regexp2.search(element[1][0]):
            if (('2') in element[1][0]) or (('2.') in element[1][0]):
                names.append(element[1][0])
                boxes.append([element[0], 'contract_number'])
        if Date_regexp.search(element[1][0]) and Date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'effective_date'])
        if Requisition_regexp.search(element[1][0]) and Requisition_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'requisition/purchase_number'])
        if Project_regexp.search(element[1][0]) and Project_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'project_number'])
        if Issued_regexp.search(element[1][0]) and Issued_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'issued_by'])
        if Admin_regexp.search(element[1][0]) and Admin_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'administered_by'])

    #returning boxes list having coordinates of all key values with their name like given below list
    # [[[651.0, 133.0], [815.0, 133.0], [815.0, 156.0], [651.0, 156.0]],effective_date]
    return boxes,names,rating


def get_first_page(result):
    # assigning all key values
    my_dict={'contract_number':'','effective_date':'','requisition/purchase_number':'','rating':'','issued_by':'',
             'administered_by':'','standard_form':'','project_number':''}
    # getting boxes for all key values with their names
    boxes, names,rating = get_key_boxes(result)
    # iterating over a result from OCR and saving a form type
    if rating!='':
        my_dict['rating']=rating
    issued_text = []
    admin_text = []
    issuedx_coordinate = ''
    issuedy_coordinate = ''
    adminx_coordinate = ''
    adminy_coordinate = ''
    issue_code = ''
    admin_code = ''
    for r in result:
        #  saving a form type
        if 'FORM' in str(r[1][0]):
            my_dict['standard_form'] = str(r[1][0]).replace('25','26')
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
                        if len(splited) == 2:
                            if splited[0] == 'CODE':
                                issue_code = "CODE: " + splited[1].replace('|', '')
                            elif splited[0] == 'Code':
                                issue_code = "CODE: " + splited[1].replace('|', '')
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
            if str(i[1]) == 'requisition/purchase_number':
                x_coordinate=301
                y_coordinate=35
            elif str(i[1])=='administered_by':
                x_coordinate = 150
                y_coordinate = 65
            else:
                x_coordinate=150
                y_coordinate=60
            # checking value which matches algo on coordinates
            if (-10 <= (r[0][0][1] - i[0][0][1]) < y_coordinate) and -20 <= (r[0][0][0] - i[0][0][0]) < x_coordinate and r[1][0] not in names:
                value=r[1][0]
                if i[1] != 'issued_by' and i[1] != 'administered_by':

                    # getting values below the key value boxes and save them to json
                    if i[1]=='effective_date':
                        value = value.replace('Mby', 'May')
                        value = value.replace('I', '1')
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
            if -8 <= (r[0][0][0] - adminx_coordinate) < 10 and 0 <= (r[0][0][1] - adminy_coordinate) <= 60:
                if r[1][0] not in admin_text:
                    admin_text.append(r[1][0])
                adminx_coordinate = r[0][0][0]
                adminy_coordinate = r[0][0][1]
        if issuedx_coordinate:
            if -8 <= (r[0][0][0] - issuedx_coordinate) < 10 and 0 <= (r[0][0][1] - issuedy_coordinate) <= 35:
                if 'NAME AND ADDRESS' not in r[1][0]:
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
        my_dict['standard_form'] = 'STANDARD FORM 26'

    return my_dict






#To get pages numbers which contain line items
def line_item_pages(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Get number of pages
        NumPages = len(pdf.pages)
        # Extract text and do the search
        target_pages=[]
        for i in range(1, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search('ITEM', Text) and re.search('SUPPLIES OR SERVICES', Text):
                target_pages.append(i+1)

    return target_pages



def get_table(pdf_path,pages):
    all_pages = ','.join(str(v) for v in pages)
    items = []
    tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=1000, pages=str(all_pages))
    #iterating over tables and manuplating values to append in items list
    for table in tables:
        try:
            df = table.df
            count=0
            try:
                df.columns=['item','supplies_or_services','unit', 'amount']
                main_index = df[df['item'] == 'ITEM'].index.tolist()
                df=df.loc[main_index[0]+1:,:]
            except:
                df.columns = ['item', 'item2','supplies_or_services', 'unit', 'amount']
                df['item']=df['item']+df['item2']
                df.drop('item2', axis=1, inplace=True)
                df.columns=['item','supplies_or_services','unit', 'amount']
                main_index = df[df['item'] == 'ITEM'].index.tolist()
                df = df.loc[main_index[0]+1:, :]

            index1=df[df['item']!=''].index.tolist()
            for i in index1:
                new_df=df.loc[i]
                df_json = new_df.to_json()
                aDict = json.loads(df_json)
                aDict['item'] = aDict['item'].replace('\n','')
                res = any(chr.isdigit() for chr in aDict['item'])
                if res:
                    if index1[-1] == i:
                        full_text = []
                        target_df = df.iloc[(i):]
                        for index, row in target_df.iterrows():
                            full_text.append(' '+row['supplies_or_services']+' '+row['unit'])
                        str1 = ' '.join(full_text)
                        name = re.compile(r'(?:\d{2,6}.\d{1,5}?-\d{1,5})|(?:\d{2,6}.\d{1,5})')
                        clauses = name.findall(str1)
                        aDict['supplies_or_services'] = str1
                        aDict['quantity'] = ''
                        aDict['unit_price'] = ''
                        aDict['clauses'] = clauses
                        items.append(aDict)
                        count += 1

                    else:
                        full_text = []
                        target_df = df.iloc[i :index1[count+1] ]
                        for index, row in target_df.iterrows():
                            full_text.append(row['supplies_or_services']+' '+row['unit'])
                        supplies = ' '.join(full_text)
                        name = re.compile(r'(?:\d{2,6}.\d{1,5}?-\d{1,5})|(?:\d{2,6}.\d{1,5})')
                        clauses = name.findall(supplies)
                        count += 1
                        aDict['supplies_or_services'] = supplies
                        aDict['quantity'] = ''
                        aDict['unit_price'] = ''
                        aDict['clauses'] = clauses
                        items.append(aDict)

        except Exception as e:
            pass
    for item_dict in items:
        supplies_text = item_dict['supplies_or_services']
        supplies_text = os.linesep.join([s for s in supplies_text.splitlines() if s])
        item_dict['supplies_or_services'] = supplies_text.replace('\n', ' ')
        item_dict['amount'] = re.sub(r'\s*[A-Za-z$]+\b', '', item_dict['amount'])

    return items





def get_clauses(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        clauses_list = []
        Months_list = ['random_x', 'JAN', 'FEB', 'MAR', "APR", 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            Text = Text.replace('DFARS', '')
            Text = Text.replace('FAR', '')
            #matching clauses pattern to get relevant line
            NumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = NumRegex.search(Text)
            #after matching pattern applied multiple conditions to extract clauses

            try:
                if array.group():
                    NumRegex2 = re.compile(r'\d{4}', flags=0)
                    NumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    lines = Text.split('\n')
                    for line in lines:
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

                        if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_next_line[-1]):
                            if not NumRegex2.search(splited_line[-1]):
                                line = line + ' ' + next_line
                                if len(line) > 20:
                                    line = line.strip()
                                    line = line.replace('(', '')
                                    line = line.replace(')', '')
                                    new_split_line = line.split(' ')
                                    if new_split_line[-2] in Months_list:
                                        new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                        new_split_line = new_split_line[:-1]
                                        line = ' '.join(new_split_line)
                                    if '/' in new_split_line[-1]:
                                        month = new_split_line[-1].split('/')[0]
                                        year = new_split_line[-1].split('/')[2]
                                        new_split_line[-1] = year + '-' + month
                                        line = ' '.join(new_split_line)
                                    clauses_list.append(line)
                        if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_third_line[-1]):
                            if (not NumRegex2.search(splited_line[-1])) and (not NumRegex2.search(splited_next_line[-1])):
                                line = line + ' ' + next_line +' '+third_line
                                if len(line) > 20:
                                    line = line.strip()
                                    line = line.replace('(', '')
                                    line = line.replace(')', '')
                                    new_split_line = line.split(' ')
                                    if new_split_line[-2] in Months_list:
                                        new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                        new_split_line = new_split_line[:-1]
                                        line = ' '.join(new_split_line)
                                    if '/' in new_split_line[-1]:
                                        month = new_split_line[-1].split('/')[0]
                                        year = new_split_line[-1].split('/')[2]
                                        new_split_line[-1] = year + '-' + month
                                        line = ' '.join(new_split_line)
                                    clauses_list.append(line)

                        if NumRegex.search(splited_line[0]) and (NumRegex2.search(splited_line[-1])):
                            if len(line) > 20:

                                line = line.replace('(', '')
                                line = line.replace(')', '')
                                new_split_line = line.split(' ')
                                if new_split_line[-2] in Months_list:
                                    new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                    new_split_line = new_split_line[:-1]
                                    line = ' '.join(new_split_line)
                                if '/' in new_split_line[-1]:
                                    month = new_split_line[-1].split('/')[0]
                                    year = new_split_line[-1].split('/')[2]
                                    new_split_line[-1] = year + '-' + month
                                    line = ' '.join(new_split_line)
                                clauses_list.append(line)

                        if NumRegex.search(splited_line[0]) and (NumRegex3.search(splited_line[-1])):
                            if len(line.split(' ')) == 2:
                                line = splited_line[0] + ' ' + lines[lines.index(line) - 1] + ' ' + lines[lines.index(line) + 1] + ' ' + splited_line[-1]
                                clauses_list.append(line)

            except Exception as e:
                pass

    #changing clauses format
    clauses_new_list = []

    for clauses in clauses_list:
        splited_clause = clauses.split(' ')
        if splited_clause[-1][0:3] in Months_list:
            splited_clause[-1]=splited_clause[-1][3:]+'-'+str(Months_list.index(splited_clause[-1][0:3]))
        if len(splited_clause[-1].split('-'))==2 and '.' not in splited_clause[-1] :
            alpharemoval = re.sub(r'\s*[A-Za-z]+\b', '', splited_clause[-1])
            splited_clause[-1] = alpharemoval.rstrip()
            updated_clause = splited_clause[0] + ' | ' + ' '.join(splited_clause[1:-1]) + ' | ' + splited_clause[-1]
            clauses_new_list.append(updated_clause)
    if len(clauses_new_list)>2:
        clauses_new_list=list(set(clauses_new_list))
    if len(clauses_new_list)==0:
        clauses_new_list=get_clauses_method2(pdf_path)
    return clauses_new_list

def get_clauses_method2(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        clauses_list = []
        Months_list = ['random_x', 'JAN', 'FEB', 'MAR', "APR", 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            Text = Text.replace('DFARS', '')
            Text = Text.replace('FAR', '')
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
                        actual_line=line
                        if line[0]==' ':
                            line=line[1:]
                        if len(line.split(' ')[0])<=5:
                            line=' '.join(line.split(' ')[1:])
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

                        if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_next_line[-1]):
                            if not NumRegex2.search(splited_line[-1]):
                                line = line + ' ' + next_line
                                if len(line) > 20:
                                    line = line.strip()
                                    line = line.replace('(', '')
                                    line = line.replace(')', '')
                                    new_split_line = line.split(' ')
                                    if new_split_line[-2] in Months_list:
                                        new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                        new_split_line = new_split_line[:-1]
                                        line = ' '.join(new_split_line)
                                    if '/' in new_split_line[-1]:
                                        month = new_split_line[-1].split('/')[0]
                                        year = new_split_line[-1].split('/')[2]
                                        new_split_line[-1] = year + '-' + month
                                        line = ' '.join(new_split_line)
                                    clauses_list.append(line)
                        if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_third_line[-1]):
                            if (not NumRegex2.search(splited_line[-1])) and (not NumRegex2.search(splited_next_line[-1])):
                                line = line + ' ' + next_line +' '+third_line
                                if len(line) > 20:
                                    line = line.strip()
                                    line = line.replace('(', '')
                                    line = line.replace(')', '')
                                    new_split_line = line.split(' ')
                                    if new_split_line[-2] in Months_list:
                                        new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                        new_split_line = new_split_line[:-1]
                                        line = ' '.join(new_split_line)
                                    if '/' in new_split_line[-1]:
                                        month = new_split_line[-1].split('/')[0]
                                        year = new_split_line[-1].split('/')[1]
                                        new_split_line[-1] = year + '-' + month
                                        line = ' '.join(new_split_line)
                                    clauses_list.append(line)

                        if NumRegex.search(splited_line[0]) and (NumRegex2.search(splited_line[-1])):
                            second_string = False
                            try:
                                next_string = lines[lines.index(actual_line) + 1]
                                next_string_split = next_string.split(' ')
                                if len(line) >= 50 and len(array_length) > 3:
                                    if (not NumRegex.search(next_string_split[0])) and  (not NumRegex.search(next_string_split[1])):
                                        second_string = True
                            except:
                                pass
                            if len(line) > 20:
                                line = line.replace('(', '')
                                line = line.replace(')', '')
                                new_split_line = line.split(' ')
                                if new_split_line[-2] in Months_list:
                                    new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                    new_split_line = new_split_line[:-1]
                                    line = ' '.join(new_split_line)
                                if '/' in new_split_line[-1]:
                                    month = new_split_line[-1].split('/')[0]
                                    year = new_split_line[-1].split('/')[1]
                                    new_split_line[-1] = year + '-' + month
                                    line = ' '.join(new_split_line)
                                if second_string==True:
                                    line=line.split(' ')
                                    line=' '.join(line[0:-1])+' '+next_string+' '+line[-1]
                                clauses_list.append(line)

                        if NumRegex.search(splited_line[0]) and (NumRegex3.search(splited_line[-1])):
                            if len(line.split(' ')) == 2:
                                line = splited_line[0] + ' ' + lines[lines.index(line) - 1] + ' ' + lines[lines.index(line) + 1] + ' ' + splited_line[-1]
                                clauses_list.append(line)

            except Exception as e:
                pass

    #changing clauses format
    clauses_new_list = []
    for clauses in clauses_list:
        splited_clause = clauses.split(' ')
        if splited_clause[-1][5:] in Months_list:
            splited_clause[-1]=splited_clause[-1][0:4]+'-'+str(Months_list.index(splited_clause[-1][5:]))
        if len(splited_clause[-1].split('-'))==2 and '.' not in splited_clause[-1] :
            alpharemoval = re.sub(r'\s*[A-Za-z]+\b', '', splited_clause[-1])
            splited_clause[-1] = alpharemoval.rstrip()
            updated_clause = splited_clause[0] + ' | ' + ' '.join(splited_clause[1:-1]) + ' | ' + splited_clause[-1]
            clauses_new_list.append(updated_clause)
    if len(clauses_new_list)>2:
        clauses_new_list=list(set(clauses_new_list))
    return clauses_new_list

def mains26(pdf_path,result):
    # for getting data from first_page
    my_dict=get_first_page(result)
    #for getting numbers of pages which have line_items
    page_number_list=line_item_pages(pdf_path)
    # #for getting line_items from table_pages
    if len(page_number_list)>1:
        line_items=get_table(pdf_path,page_number_list)
    else:
        line_items=[]
    my_dict['items']=line_items
    my_dict['clauses']=get_clauses(pdf_path)
    # #for returning response
    return my_dict


