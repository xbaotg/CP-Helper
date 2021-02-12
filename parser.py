import requests
import sys
import os
from shutil import copyfile
from bs4 import BeautifulSoup


INVALID_LINK = "Your link is invalid"


def read_url_from_input():
    return input("CodeForces Link: ")


def throw_error(msg):
    print("------------------------")
    print(msg)
    print("------------------------")
    sys.exit(0)



def process():
    url = read_url_from_input()
    #url = "https://codeforces.com/problemset/problem/996/A"

    response = requests.get(url)

    if response.status_code != 200:
        throw_error(INVALID_LINK)

    text = response.text

    if "codeforces.com/problemset/problem" in url:
        try:
            soup = BeautifulSoup(text, features="lxml")
            sample_text_element = soup.find("div", {"class": "sample-test"})

            cwd = os.getcwd()
            create = soup.title.text.split(" - ")[1]

            # create root folder if not exists
            if not os.path.exists(os.path.join(cwd, create)):
                os.mkdir(os.path.join(cwd, create))

            cwd = os.path.join(cwd, create)

            # create testcases folder if not exists
            if not os.path.exists(os.path.join(cwd, "testcases")):
                os.mkdir(os.path.join(cwd, "testcases"))

            cwd = os.path.join(cwd, "testcases")

            for index, input_element in enumerate(sample_text_element.find_all("div", {"class": "input"})):
                input_value = input_element.find("pre").get_text()

                with open(os.path.join(cwd, f"sample-input-{index + 1}"), "w+") as f:
                    f.write(input_value.strip())
                    f.close()

            for index, output_element in enumerate(sample_text_element.find_all("div", {"class": "output"})):
                output_value = output_element.find("pre").get_text()

                with open(os.path.join(cwd, f"sample-output-{index + 1}"), "w+") as f:
                    f.write(output_value.strip())
                    f.close()

            # create file from templates
            cwd = os.path.join(os.getcwd(), create)

            copyfile(os.path.join(os.getcwd(), "template.cpp"), os.path.join(cwd, "main.cpp"))

        except:
            throw_error(INVALID_LINK)
    else:
        throw_error(INVALID_LINK)


process()
