
import requests
import shutil
from subprocess import PIPE, Popen
import lxml.html
from time import sleep
import re
from getpass import getpass
import json
import sys

param = json.load(open('config.json'))
username = param['username']
password = getpass("password: ")

sem_num     = param['sem_num'] # example: "2015-2016-1"
course_id   = param['course_id'] # example: "40231162"
sub_id      = param['sub_id'] # example: "0"
freq        = param['freq']
course_type = param['course_type'] # example: rx, ty, bx, cx, xx

csn = {}
csn["rx"] = 'p_rx_id'
csn["bx"] = 'p_bxk_id'
csn["ty"] = 'p_rxTy_id'
csn["xx"] = 'p_xxk_id'
csn["cx"] = 'p_cxk_id';

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
        try:
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
        except Exception as e:
            print e
            print 'pass.'

    try:
        data = s.get("http://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do?m=%sSearch&p_xnxq=%s" % (course_type, sem_num)).text
        html = lxml.html.fromstring(data)
        formV = extractForm(html.forms[0])
        formV['p_kch'] = course_id
        formV['page'] = '-1'
        formV['m'] = "%sSearch" % course_type
        
        # trInfo = re.search(ur'<tr class="trr2">.*?</tr>', data, re.DOTALL + re.UNICODE).group(0)
        # don't know how to make this work
        # print lxml.etree.tostring(lxml.html.fromstring(trInfo), method="text")
    except Exception as e:
        print e
        print 'pass.'

    displayed = 0
    while True:
        try:
            data = s.post('http://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do', data=formV).text
            tbl = re.search(r'(<table.*?trr1.*?</table>).*?(<table.*?trr2.*?</table>)', data, re.DOTALL)
            if not tbl:
                print "Session timeout!"
                break

            if displayed == 0:
                displayed = 1
                tbRes = lxml.html.fromstring(tbl.group(2))
                for td in tbRes.cssselect('td'):
                    print td.text_content().replace("\n", "").replace(" ", "")

            tbRes = lxml.html.fromstring(tbl.group(2))
            ind = 0
            for td in tbRes.cssselect('td'):
                ind += 1
                if ind == 5:
                    left = td.text_content()
                    break

            if left != "0":
                html = lxml.html.fromstring(data)
                formV = extractForm(html.forms[0])
                formV['m'] = "save%sKc" % course_type.title()
                formV[csn[course_type]] = "%s;%s;%s;" % (sem_num, course_id, sub_id)
                data = s.post('http://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do', data=formV).text
                print re.search(r'showMsg\((.*)\)', data).group(1)
                exit(0)
            else:
                attemptCnt += 1
                print str(attemptCnt) + " attempt(s) failed."
                sleep(freq)
        except Exception as e:
            print e
            print "pass."

