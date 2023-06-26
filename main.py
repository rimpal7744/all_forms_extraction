from fastapi import FastAPI, File, UploadFile
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from s26_scraper import mains26
from s30_scraper import mains30
from s33_scraper import main
from s1449_scraper import main_1449
import uvicorn
import numpy as np
from s1155 import mains1155
import os
import re
import uuid
from checking_type import type_of_pdf
ocr = PaddleOCR(use_angle_cls=True, lang='en', enable_mkldnn=True) # need to run only once to download and load model into memory

app = FastAPI()


@app.post("/upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"{(str(uuid.uuid1())+'.pdf')}"
    # file_location = f"{(str(uuid.uuid1())+'first_page.pdf')}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    images = convert_from_path(file_location,last_page=1)

    pix = np.array(images[0])
    result = ocr.ocr(pix, cls=True)
    result = result[0]

    #Different regex to detect which form it is
    form30regexp = re.compile(r'(FORM 30)|(FORM30)')
    form33regexp = re.compile(r'(FORM 33)|(FORM33)')
    form26regexp = re.compile(r'(FORM 26)|(FORM26)|(FORM 25)|(FORM25)|(Form 26)|(Form 25)')
    form1449regexp = re.compile(r'(FORM 1449)|(FORM1449)')
    form1155regexp = re.compile(r'(FORM 1155)|(FORM1155)|(F0RM 1155)|(F0RM1155)')

    Parse=False
    final_result={}
    form_type=''

    for line in result:
        if 'STANDARD FORM' in str(line[1][0]).upper():
            form_type=str(line[1][0])
        elif ('DD FORM' in str(line[1][0]).upper()) or ('DD F0RM' in str(line[1][0]).upper()):
            form_type = str(line[1][0])
    #checking form type and implement method accordingly
    if form_type != '':
        type_of_pdf(file_location)
        if form26regexp.search(form_type):
            print('26form')
            final_result=mains26(file_location,result)
            Parse=True


        elif form30regexp.search(form_type):
            print('30form')
            final_result=mains30(result)
            Parse=True


        elif form33regexp.search(form_type) :
            print('33form')
            final_result=main(file_location,result)
            # final_result=main33(file_location,result)
            Parse=True

        elif form1449regexp.search(form_type):
            print('1449form')
            final_result=main_1449(result)
            Parse=True

        elif form1155regexp.search(form_type.upper()):
            print('form1155')
            final_result=mains1155(file_location,result)
        else:
            pass


    #in some cases form type not detected in sf30, this execution will take place
    if Parse==False:
        for line in result:
            Amendmentregexp = re.compile(r'(AMENDMENT)')
            Amendmentregexp2 = re.compile(r'(NO)|(NUMBER)')
            if Amendmentregexp.search(line[1][0]) and Amendmentregexp2.search(line[1][0]):
                print('30form')
                final_result = mains30(result)

    os.remove(file_location)
    if final_result=={}:
        final_result={'Invalid Form Type'}
    return final_result



