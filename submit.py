from robobrowser import RoboBrowser
import pickle, os, colorama, sys, time
import requests

args = sys.argv[1:]
browser = RoboBrowser(parser='html.parser')
code = {
    "cpp": "42",
    "py": "31",
    "java": "36",
    "pas": "4"
}
username = "tgbaodeeptry"
password = "Bao270304"


def login():
    rcpc = open(os.path.join(os.path.dirname(__file__), "rcpc"), "r").readline()

    browser.session.cookies["RCPC"] = rcpc
    browser.open('http://codeforces.com/enter')

    print(browser.parsed)

    enter_form = browser.get_form('enterForm')
    enter_form['handleOrEmail'] = username
    enter_form['password'] = password
    enter_form['remember'].options = [True]
    enter_form['remember'].value = True

    browser.submit_form(enter_form)

    with open(os.path.join(os.path.dirname(__file__), "session"), 'wb') as f:
        pickle.dump(browser.session.cookies, f)


def safe_get(dct, key):
    try:
        dct = dct[key]
    except KeyError:
        return None
    return dct


def get_latest_verdict(user):
    r = requests.get('http://codeforces.com/api/user.status?' +
                     'handle={}&from=1&count=1'.format(user))
    js = r.json()
    if 'status' not in js or js['status'] != 'OK':
        raise ConnectionError('Cannot connect to codeforces!')
    try:
        result = js['result'][0]
        id_ = result['id']
        verdict_ = safe_get(result, 'verdict')
        time_ = result['timeConsumedMillis']
        memory_ = result['memoryConsumedBytes'] / 1000
        passedTestCount_ = result['passedTestCount']
    except Exception as e:
        raise ConnectionError('Cannot get latest submission, error')
    return id_, verdict_, time_, memory_, passedTestCount_


if len(args):
    print("------------------------------")
    path = args[0]
    params = path.split("/")
    problem_code = "".join(params[-3:-1]).upper()
    file_codes = "\n".join(open(path).readlines())
    last_id, b, c, d, e = get_latest_verdict(username)

    print(colorama.Fore.WHITE + "+ " + colorama.Fore.GREEN + "Submitting.... " + colorama.Fore.RESET, end="")

    if not os.path.exists(os.path.join(os.path.dirname(__file__), "session")):
        login()
    else:
        with open(os.path.join(os.path.dirname(__file__), "session"), 'rb') as f:
            browser.session.cookies.update(pickle.load(f))

    ok = False

    while True:
        try:
            browser.open('https://codeforces.com/')

            csrf = browser.select('.csrf-token')[0]["data-csrf"]
            url = f"http://codeforces.com/contest/{problem_code[:-1]}/submit?csrf_token={csrf}"

            data = {
                "csrf_token": csrf,
                "action": "submitSolutionFormSubmitted",
                "contestId": problem_code[:-1],
                "submittedProblemIndex": problem_code[-1],
                "programTypeId": code[params[-1][(params[-1].find(".") + 1):]],
                "source": file_codes,
                "tabSize": "4",
                "sourceFile": ""
            }

            res = browser.session.post(url=url, data=data)

            if res.status_code != 200:
                login()
                continue

            if "/my" in res.url:
                print(colorama.Fore.LIGHTGREEN_EX + "Ok")
                ok = True
            else:
                print(colorama.Fore.RED + "Same")

            break
        except Exception as e:
            login()

    if ok == True:
        print(colorama.Fore.WHITE + "+ " + colorama.Fore.GREEN + "Checking result... " + colorama.Fore.RESET, end="")

        # check result
        hasStarted = False

        while True:
            id_, verdict_, time_, memory_, passedTestCount_ = get_latest_verdict(username)
            if id_ != last_id and verdict_ != 'TESTING' and verdict_ is not None:
                if verdict_ == 'OK':
                    print(colorama.Fore.LIGHTGREEN_EX + "Ok")
                    print(colorama.Fore.WHITE + "+ " + colorama.Fore.GREEN + "Info: ")
                    print(colorama.Fore.BLUE + "   - Passed {} tests".format(passedTestCount_))
                    print(colorama.Fore.BLUE + "   - {} MS | {} KB".format(time_, memory_) + colorama.Fore.RESET)
                else:
                    print(colorama.Fore.RED + verdict_)
                    print(colorama.Fore.WHITE + "+ " + colorama.Fore.GREEN + "Info: ")
                    print(colorama.Fore.BLUE + "   - Wrong on test {}".format(passedTestCount_ + 1))
                    print(colorama.Fore.BLUE + "   - {} MS | {} KB".format(time_, memory_) + colorama.Fore.RESET)
                break
            elif verdict_ == 'TESTING' and (not hasStarted):
                hasStarted = True

            time.sleep(0.5)
    print("------------------------------")
