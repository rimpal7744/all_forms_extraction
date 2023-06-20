import re

def get_key_boxes(result):
    #match regex for all key values from OCR result and get their boxes
    boxes=[]
    #to append names given in forms for key values
    names=[]
    for element in result:
        #all regex matching for keys respectively
        Amendmentregexp = re.compile(r'(AMENDMENT)')
        Amendmentregexp2 = re.compile(r'(NO)|(NUMBER)')
        Contractregexp = re.compile(r'(CONTRACT)|(CONIRACT)')
        Contractregexp2 = re.compile(r'(CODE)')
        Dateregexp = re.compile(r'(EFFECTIVE)|(EFFECIVE)')
        Dateregexp2 = re.compile(r'(DATE)|(DAIE)')
        Requisitionregexp = re.compile(r'(REQUISITION)')
        Requisitionregexp2 = re.compile(r'(NO)|(NUMBER)')
        Projectregexp = re.compile(r'(PROJECT)')
        Projectregexp2 = re.compile(r'(NO)|(NUMBER)')
        Issuedregexp = re.compile(r'(ISSUED)')
        Issuedregexp2 = re.compile(r'(BY)|(8Y)')
        Adminregexp = re.compile(r'(ADMINISTERED)')
        Adminregexp2 = re.compile(r'(BY)|(8Y)')
        if Amendmentregexp.search(element[1][0]) and Amendmentregexp2.search(element[1][0]):
            if '2' in element[1][0]:
                names.append(element[1][0])
                boxes.append([element[0], 'amendment_no'])
        if Contractregexp.search(element[1][0]) and Contractregexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'contract_code'])
        if Dateregexp.search(element[1][0]) and Dateregexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'effective_date'])
        if Requisitionregexp.search(element[1][0]) and Requisitionregexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'requisition/purchase_number'])
        if Projectregexp.search(element[1][0]) and Projectregexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'project_number'])
        if Issuedregexp.search(element[1][0]) and Issuedregexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'issued_by'])
        if Adminregexp.search(element[1][0]) and Adminregexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'administered_by'])

    #returning boxes list having coordinates of all key values with their name like given below list
    # [[[651.0, 133.0], [815.0, 133.0], [815.0, 156.0], [651.0, 156.0]],effective_date]
    return boxes,names


def get_first_page(result):
    #assigning all key values
    my_dict={'contract_code':'','amendment_no':'','effective_date':'','requisition/purchase_number':'','project_number':'','issued_by':'','administered_by':'','standard_form':''}

    #getting boxes for all key values with their names
    boxes,names=get_key_boxes(result)

    # iterating over a result from OCR and saving a form type
    for line in result:
        if 'FORM' in str(line[1][0]):
            my_dict['standard_form']=str(line[1][0])

    issued_text = []
    admin_text=[]
    issuedx_coordinate = ''
    issuedy_coordinate = ''
    adminx_coordinate = ''
    adminy_coordinate = ''
    issue_code=''
    admin_code=''
    for r in result:
        for i in boxes:
            # algo for getting CODE value in adminstered by
            if admin_code=='':
                if i[1]=='administered_by':
                    Adminregexp = re.compile(r'(ADMINISTERED)')
                    Adminregexp2 = re.compile(r'(BY)|(8Y)')
                    if Adminregexp.search(r[1][0]) and Adminregexp2.search(r[1][0]):
                        present = result.index(r)
                        admin_string=result[present+2][1][0]
                        digit = 0
                        for ch in admin_string:
                            if ch.isdigit():
                                digit = digit + 1
                        if digit>=3 or len(admin_string.split(' '))==1:
                            admin_code='Code: '+result[present+2][1][0].replace('|','')
            # algo for getting CODE value in adminstered by
            if issue_code=='':
                if i[1] == 'issued_by':
                    Issuedregexp = re.compile(r'(ISSUED)')
                    Issuedregexp2 = re.compile(r'(BY)|(8Y)')
                    if Issuedregexp.search(r[1][0]) and Issuedregexp2.search(r[1][0]):
                        present = result.index(r)
                        splited=result[present+1][1][0].split(' ')
                        if len(splited)==2:
                            if splited[0]=='CODE':
                                issue_code="CODE: "+splited[1].replace('|','')
                        if issue_code=='':
                            issued_string=result[present+2][1][0]
                            digit = 0
                            for ch in issued_string:
                                if ch.isdigit():
                                    digit = digit + 1
                            if digit>=3 or len(issued_string.split(' '))==1:
                                issued_string=issued_string.replace('|','')
                                issue_code='CODE: '+ issued_string


            if (0 <= (r[0][0][1] - i[0][0][1]) < 60) and -20 <= (r[0][0][0] - i[0][0][0]) < 120 and r[1][0] not in names:
                if i[1]!='issued_by' and i[1]!='administered_by':
            # getting values below the key value boxes and save them to json
                    my_dict[i[1]]=r[1][0]
            #issued_by and adminstered by have large values so combining all values to issued_text and admin_text
                if i[1] == 'issued_by':
                    issuedx_coordinate = r[0][0][0]
                    issuedy_coordinate = r[0][0][1]
                    issued_text.append(issue_code)
                if i[1] == 'administered_by':
                    adminx_coordinate = r[0][0][0]
                    adminy_coordinate = r[0][0][1]
                    admin_text.append(admin_code)
        if adminy_coordinate:
            if -8<=(r[0][0][0]-adminx_coordinate)<10 and 0<=(r[0][0][1]-adminy_coordinate)<=60:
                admin_text.append(r[1][0])
                adminx_coordinate = r[0][0][0]
                adminy_coordinate = r[0][0][1]
        if issuedx_coordinate:
            if -8<=(r[0][0][0]-issuedx_coordinate)<10 and 0<=(r[0][0][1]-issuedy_coordinate)<=35:
                issued_text.append(r[1][0])
                issuedx_coordinate = r[0][0][0]
                issuedy_coordinate = r[0][0][1]
    #joining issued_text and administered_text to feed in json
    if len(issued_text)>0:
        my_dict['issued_by']='\n'.join(issued_text)
    if len(admin_text)>0:
        my_dict['administered_by'] = '\n'.join(admin_text)
    if my_dict['standard_form']=='':
        my_dict['standard_form']='STANDARD FORM 30'
    return my_dict


def mains30(result):
    #to get data from first page
    mydict=get_first_page(result)
    return mydict

