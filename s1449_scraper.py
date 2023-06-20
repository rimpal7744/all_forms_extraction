import re

def get_key_boxes(result):
    #match regex for all key values from OCR result and get their boxes
    boxes=[]
    #to append names given in forms for key values
    names=[]
    for element in result:
        #all regex matching for keys respectively
        Contract_regexp = re.compile(r'(CONTRACT)|(CONIRACT)|(Contract)')
        Contract_regexp2 = re.compile(r'(NO)|(NO.)|(NUMBER)|(no.)|(No.)')
        Date_regexp = re.compile(r'(EFFECTIVE)|(EFFECIVE)|(Effective)')
        Date_regexp2 = re.compile(r'(AWARD)|(DATE)|(DAIE)|(Date)')
        Requisition_regexp = re.compile(r'(PURCHASE)|(REQUISITION)|(Requisition)|(Purchase)')
        Requisition_regexp2 = re.compile(r'(NO)|(NUMBER)|(NO.)|(No.)')
        Order_regexp = re.compile(r'(ORDER)')
        Order_regexp2 = re.compile(r'(NO)|(NUMBER)')
        Soliciation_regexp = re.compile(r'(SOLICITATION)|(SOLICITAIION)')
        Soliciation_regexp2 = re.compile(r'(NUMBER)|(NO.)')
        Soliciation_issue_regexp = re.compile(r'(SOLICITATION)|(SOLICITAIION)')
        Soliciation_issue_regexp2 = re.compile(r'(ISSUE)|(Issue)')
        Issued_regexp = re.compile(r'(ISSUED)|(Issued)')
        Issued_regexp2 = re.compile(r'(BY)|(8Y)|(By)')
        Admin_regexp = re.compile(r'(ADMINISTERED)|(Administered)')
        Admin_regexp2 = re.compile(r'(BY)|(8Y)|(By)')
        Name_regexp = re.compile(r'(NAME)')
        Name_regexp2 = re.compile(r'(a.)')
        Tele_regexp = re.compile(r'(TELEPHONE)')
        Tele_regexp2 = re.compile(r'(NUMBER)')
        Offer_regexp = re.compile(r'(OFFER)')
        Offer_regexp2 = re.compile(r'(DUE)|(8.)')
        Award_regexp = re.compile(r'(AWARD)')
        Award_regexp2 = re.compile(r'(AMOUNT)')
        Account_regexp = re.compile(r'(ACCOUNTING)|(APPROPRIATION)')
        Account_regexp2 = re.compile(r'(DATA)')

        if Contract_regexp.search(element[1][0]) and Contract_regexp2.search(element[1][0]):
            if (('2') in element[1][0]) or (('2.') in element[1][0]):
                names.append(element[1][0])
                boxes.append([element[0], 'contract_number'])
        if Date_regexp.search(element[1][0]) and Date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'effective_date'])
        if Requisition_regexp.search(element[1][0]) and Requisition_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'requisition_number'])
        if Order_regexp.search(element[1][0]) and Order_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'order_number'])
        if Soliciation_regexp.search(element[1][0]) and Soliciation_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'soliciation_number'])
        if Soliciation_issue_regexp.search(element[1][0]) and Soliciation_issue_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'soliciation_date'])
        if Issued_regexp.search(element[1][0]) and Issued_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'issued_by'])
        if Admin_regexp.search(element[1][0]) and Admin_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'administered_by'])
        if Name_regexp.search(element[1][0]) and Name_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'name'])
        if Tele_regexp.search(element[1][0]) and Tele_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'telephone_no'])
        if Offer_regexp.search(element[1][0]) and Offer_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'offer_due'])
        if Award_regexp.search(element[1][0]) and Award_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'award_amount'])
        if Account_regexp.search(element[1][0]) and Account_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'accounting_data'])
    #returning boxes list having coordinates of all key values with their name like given below list
    # [[[651.0, 133.0], [815.0, 133.0], [815.0, 156.0], [651.0, 156.0]],effective_date]
    return boxes,names


def get_first_page(result):
    my_dict = {'contract_number': '', 'effective_date': '', 'requisition_number': '', 'order_number': '','soliciation_number': '',
               'soliciation_date':'','issued_by': '','name':'','telephone_no':'','offer_due':'',
               'award_amount':'','accounting_data':'','standard_form': ''}
    boxes,names=get_key_boxes(result)

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
            my_dict['standard_form'] = str(r[1][0]).replace('25', '26')
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
            min_y_coordinate=-10
            if str(i[1]) == 'requisition_number':
                max_x_coordinate = 301
                max_y_coordinate = 35
            elif str(i[1]) == 'administered_by':
                max_x_coordinate = 150
                max_y_coordinate = 65
            elif str(i[1])=='name' or str(i[1])=='telephone_no' or str(i[1])=='offer_due' or str(i[1])=='soliciation_date':
                min_y_coordinate=35
                max_x_coordinate=150
                max_y_coordinate=100
            else:
                min_y_coordinate=-10
                max_x_coordinate = 150
                max_y_coordinate = 70

            # checking value which matches algo on coordinates
            if (min_y_coordinate <= (r[0][0][1] - i[0][0][1]) < max_y_coordinate) and -20 <= (r[0][0][0] - i[0][0][0]) < max_x_coordinate and r[1][0] not in names:
                value = r[1][0]
                if i[1] != 'issued_by' and i[1] != 'administered_by':
                    # getting values below the key value boxes and save them to json
                    if i[1] == 'effective_date':
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
            if -8 <= (r[0][0][0] - issuedx_coordinate) < 10 and 0 <= (r[0][0][1] - issuedy_coordinate) <= 60:
                if 'NAME AND ADDRESS' not in r[1][0] and '11.' not in r[1][0]:
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
        my_dict['standard_form'] = 'STANDARD FORM 1449'

    return my_dict


def main_1449(result):
    #getting_data_from_first_page
    mydict=get_first_page(result)
    return mydict