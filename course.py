
import requests
import shutil
from subprocess import PIPE, Popen
import lxml.html
from time import sleep
import re
from getpass import getpass

# TODO: fill the blanks before using
username = ""
password = getpass("password: ")

sem_num     = "" # example: "2015-2016-1"
course_id   = "" # example: "40231162"
sub_id      = "" # example: "0"

captcha = 'http://zhjwxk.cic.tsinghua.edu.cn/login-jcaptcah.jpg?captchaflag=login1'
loginPost = "https://zhjwxk.cic.tsinghua.edu.cn/j_acegi_formlogin_xsxk.do"
userAgent = {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}

def getCaptcha(s):
    response = s.get(captcha, stream=True)
    with open('1.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

def extractForm(form):
    formV = {}
    for input in form.inputs:
        if input.name == None or input.get("type") == "checkbox" or input.get("type") == "submit" or input.get("type") == "image":
            continue
        if input.value == None:
            formV[input.name] = ""
        else:
            formV[input.name] = input.value
    return formV

s = requests.session()
left = 0
attemptCnt = 0

while True:
    # login
    while True:
        s.get('http://zhjwxk.cic.tsinghua.edu.cn/xklogin.do', headers=userAgent, verify=False, timeout=10)
        getCaptcha(s)
        p = Popen(["python", "captcha.py"], stdout=PIPE)
        captchaCode = p.communicate()[0][0:4]
        form = {'j_username': username, 'j_password': password, 'captchaflag': 'login1', '_login_image_': captchaCode}
        response = s.post(loginPost, data=form, headers=userAgent, verify=False, timeout=10)
        print "captcha guess = " + captchaCode
        if (response.url.find('login_error=code_error')) > 0:
            continue
        elif (response.url.find('login_error')) > 0:
            print "** Please recheck your username and password!"
            exit(1)
        else:
            print "Succeeded!"
            break

    data = s.get("http://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do?m=rxSearch&p_xnxq=%s" % sem_num).text
    html = lxml.html.fromstring(data)
    formV = extractForm(html.forms[0])
    formV['p_kch'] = course_id
    formV['page'] = '-1'
    formV['m'] = 'rxSearch'

    while True:
        data = s.post('http://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do', data=formV).text
        if data.find('table_t') < 0:
            print "Session timeout!"
            break
        html = lxml.html.fromstring(data)
        tbRes = html.get_element_by_id('table_t')
        ind = 0
        for td in tbRes.cssselect('td'):
            ind += 1
            if ind == 5:
                left = td.text_content()
                break

        if left != "0":
            html = lxml.html.fromstring(data)
            formV = extractForm(html.forms[0])
            formV['m'] = 'saveRxKc'
            formV['p_rx_id'] = "%s;%s;%s;" % (sem_num, course_id, sub_id)
            data = s.post('http://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do', data=formV).text
            print re.search(r'showMsg\((.*)\)', data).group(1)
            exit(0)
        else:
            attemptCnt += 1
            print str(attemptCnt) + " attempt(s) failed."
            sleep(1)

