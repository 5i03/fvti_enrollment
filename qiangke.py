import requests
import os
import subprocess
import platform
import threading


class Enrollment:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.88 Safari/537.36'
        }

    def verify_code(self):
        cap_url = 'http://10.1.1.100/studentportal.php/Public/verify/'
        r = self.session.get(cap_url, verify=False)
        capimg = r.content
        with open('captcha.png', 'wb') as f:
            f.write(capimg)
        print("验证码已保存,请打开软件所在目录查看“captcha.png”并输入")
        filepath = os.path.join(os.getcwd(), 'captcha.png')
        if platform.system() == 'Darwin':
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':
            os.startfile(filepath)
        else:
            subprocess.call(('xdg-open', filepath))
        self.code = input("在此输入：")
        os.remove('captcha.png')
        return 1

    def login(self, stu_id, stupwd):
        login_url = 'http://10.1.1.100/studentportal.php/Index/checkLogin'
        res = self.session.post(login_url, data={
            "logintype": "xsxh", 'xsxh': stu_id, 'dlmm': stupwd, 'yzm': self.code}, verify=False).json()
        if res['code'] == 3:
            print('验证码错误！')
            return 0
        elif res['code'] == 0:
            return 1
        else:
            print(res)
            print('登录异常, 未知错误！')
            exit()

    def course_info(self):
        course_url = 'http://10.1.1.100/studentportal.php/Wsxk/yjxklb/'
        courselist = []
        res = self.session.post(course_url, data={"page": "1", "rows": "50"}, verify=False).json()['rows']
        for i, data in enumerate(res):
            courselist.append(data['id'])
            print(
                f"{i + 1}. | 课名： {data['kcmc']} | 老师： {data['zdjsxm']} | 课号： {data['id']} | 学时： {data['xqzxs']} | 余位: {int(data['xkrsrl']) - int(data['xkyxrs'])}")
        return courselist

    def enroll_thread(self, course_id):
        enroll_url = 'http://10.1.1.100/studentportal.php/Wsxk/yjxkbc'
        response = self.session.post(enroll_url, data={'xkxxid': course_id, 'xktjid': 0}).json()
        if response["Code"] == '0':
            print('抢课',course_id,'失败,是因为',response["errorMsg"])
        elif response["Code"] == '1':
            print('抢课',course_id,"成功,还可选",str(4-int(response["rxkxsyxs"])),"门")
        else:
            print(response)
            # print(response["Code"])
            pass

if __name__ == "__main__":
    c = Enrollment()
    print('开始登录')
    while True:
        # 教务系统学号密码
        stu_id = ""
        stu_pwd = ""
        if c.verify_code() and c.login(stu_id, stu_pwd):
            print('登录成功！学号：' + stu_id + '，请稍后\n' + '即将进入选课系统！')
            xkid = c.course_info()
            threads = []
            while True:
                courseid = int(input("请输入课程序号(0退出）："))

                if courseid == 0:
                    break
                if courseid <= len(xkid):
                    courseId = xkid[courseid - 1]
                    thread = threading.Thread(target=c.enroll_thread, args=(courseId,))
                    thread.start()
                    threads.append(thread)
                else:
                    print("没有对应课程！再试一次？")

            for thread in threads:
                thread.join()
            break
        else:
            print('即将重新登录, 请等待...')
