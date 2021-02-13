import requests
import sys
import os
from shutil import copyfile
from bs4 import BeautifulSoup

INVALID_LINK = "Your link is invalid"


def read_url_from_input():
    return input("Link: ")


def throw_error(msg):
    print("------------------------")
    print(msg)
    print("------------------------")
    sys.exit(0)


def generate_data_dir(root_path, name_dir):
    """
    Generate data dir that contains testcases dir, and file code

    :param root_path:
    :return:
    """

    path_dir = os.path.join(root_path, name_dir)

    if not os.path.exists(path_dir):
        os.mkdir(path_dir)

    path_testcases = os.path.join(path_dir, "testcases")

    # create testcases folder if not exists
    if not os.path.exists(path_testcases):
        os.mkdir(path_testcases)

    return path_dir, path_testcases


def write_to_file(file, value):
    with open(file, "w+") as f:
        f.write(value)
        f.close()


def process():
    url = read_url_from_input()
    # url = "https://codeforces.com/problemset/problem/996/A"
    # url = "https://atcoder.jp/contests/abc191/tasks/abc191_b"

    response = requests.get(url)

    if response.status_code != 200:
        throw_error(INVALID_LINK)

    # Base Setup
    text = response.text
    soup = BeautifulSoup(text, features="lxml")
    name_dir = ""
    root_dir = os.getcwd()
    data_input_output = []
    good_link = False

    if "codeforces.com/problemset/problem" in url:
        try:
            name_dir = soup.title.text.split(" - ")[1]

            # find elements
            sample_text_element = soup.find("div", {"class": "sample-test"})

            for index, input_element in enumerate(sample_text_element.find_all("div", {"class": "input"})):
                input_value = input_element.find("pre").get_text().strip()
                data_input_output.append([input_value])

            for index, output_element in enumerate(sample_text_element.find_all("div", {"class": "output"})):
                output_value = output_element.find("pre").get_text().strip()
                data_input_output[index].append(output_value)

            good_link = True
        except:
            throw_error(INVALID_LINK)

    # AtCoder
    elif "atcoder.jp/contests/" in url:
        try:
            contest_name = url.split("/")[-3]
            name_dir = url.split("/")[-1].replace(contest_name + "_", "")

            root_dir = os.path.join(os.getcwd(), contest_name)

            if not os.path.exists(root_dir):
                os.mkdir(root_dir)

            for idx, part in enumerate(soup.select('span[class="lang-en"] > div[class="part"] > section > pre')):
                value = part.get_text().strip()

                if idx % 2 == 0:
                    data_input_output.append([value])
                else:
                    data_input_output[idx // 2].append(value)

            good_link = True
        except:
            throw_error(INVALID_LINK)

    if good_link:
        data_dir, testcases_dir = generate_data_dir(root_dir, name_dir)

        for idx, x in enumerate(data_input_output, start=1):
            input_value, output_value = x[0], x[1]

            write_to_file(os.path.join(testcases_dir, f"sample-input-{idx}"), input_value)
            write_to_file(os.path.join(testcases_dir, f"sample-output-{idx}"), output_value)

        # create file from templates
        path_file_parser = os.path.dirname(os.path.abspath(__file__))
        copyfile(os.path.join(path_file_parser, "template.cpp"), os.path.join(data_dir, "main.cpp"))

        print("Created folder: " + os.path.dirname(data_dir))

process()
