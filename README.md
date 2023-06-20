# extraction_test

## Scraper for PDF form sf33,sf26,sf30

To run this install all required packages with below command

pip3 install -r requirement.txt

run python3 main.py

Above command will run Fast api app. Dont forget to add /upload-file/ with your url to hit it and upload file in file tag in body.


# Run it through Docker

## run below commands:
docker build --tag <your_image_name> .

docker build --tag python-docker .

(you can replace python-docker with your custome name for image)

to run docker docker run <your_image_name>

docker run python-docker
