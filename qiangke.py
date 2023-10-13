import time  # 时间模块
import requests  # 网络请求模块
import os  # 系统模块
import re  # 正则表达式模块
# from crypto.Cipher import DES  # 加密模块
import base64  # base64模块
import logging  # 日志模块
import subprocess
import platform
class enrollment:
    
    def __init__(self, ):  # 初始化
        # logging.basicConfig() # 日志配置
        self.session = requests.Session()  # 创建会话
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}  # 设置请求头

    # 验证码处理
    def verfiyCode(self):
        capURL='http://10.1.1.100/studentportal.php/Public/verify/'
        r = self.session.get(capURL, verify=False)
        capimg = r.content
        with open('captcha.png', 'wb') as f:
            f.write(capimg)
        print("验证码已保存,请打开软件所在目录查看“captcha.png”并输入")
        # 打开captcha.png
        # os.open()
        filepath = os.path.join(os.getcwd(), 'captcha.png')
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(filepath)
        else:  # linux variants
            subprocess.call(('xdg-open', filepath))
        self.code = input("在此输入：")
        os.remove('captcha.png')
        return 1

    # 登录
    def login(self, stuid, stupwd):
        loginURL='http://10.1.1.100/studentportal.php/Index/checkLogin'
        res = self.session.post(loginURL, data={
                                "logintype": "xsxh", 'xsxh': stuid, 'dlmm': stupwd, 'yzm': self.code}, verify=False).json()
        if res['code'] == 3:
            print('验证码错误！')
            return 0
        elif res['code'] == 0:
            return 1
        else:
            print(res)
            print('登录异常, 出现未知错误！')
            time.sleep(3)
            exit()

    # 获取选修课列表
    def courseInfo(self):
        courseURL='http://10.1.1.100/studentportal.php/Wsxk/yjxklb/'
        courselist = []
        res = self.session.post(courseURL, data={
                                "page": "1", "rows": "50"}, verify=False).json()['rows']
        for i, list in enumerate(res):

            id = list['id']  # 抢课软件显示序列号
            courselist.append(id)
            name = list['kcmc']   # 课程名称
            tech = list['zdjsxm']  # 任课老师姓名
            # leixin = list["kcflmc"]
            rang = list["kkxqmc"]  # 上课区域
            xkid = list["xkxxid"]  # 提交的选修课ID
            xqzxs = list["xqzxs"]  # 可以获得的学时
            xkrsrl = list["xkrsrl"]# 限制选定人数
            xkyxrs= list["xkyxrs"]# 已选定人数
            # print(f"{i + 1}.{name} {tech} {leixin} {rang}")
            print(f"{i + 1}.  |课名： {name}  |老师： {tech} |课号： {xkid} |学时： {xqzxs} | 余位："+ str(int(xkrsrl)-int(xkyxrs)))
        return courselist

    # 发送请求数据
    def processingData(self, ID):
        enrollURL='http://10.1.1.100/studentportal.php/Wsxk/yjxkbc'
        reponse = self.session.post(enrollURL, data={'xkxxid': ID, 'xktjid': 0}).json()
        if reponse["Code"] == 0:
            print(reponse["errorMsg"])
        elif reponse["Code"] == 1:
            print('恭喜你成功抢到课了！')
        else:
            time.sleep(1)
            print(reponse)


if __name__ == "__main__":

    c = enrollment()
    print('开始登录')
    while True:
        # 登录
        stuID = ""  # 教务系统学号
        stuPass = ""  # 教务系统密码

        if c.verfiyCode() and c.login(stuID, stuPass):
            print('登录成功！学号：'+stuID+'密码：'+stuPass + '，请稍后\n'+'即将进入选课系统！')
            xkid = c.courseInfo()
            while True:
                courseid = int(input("请输入课程序号(0退出）："))  # 输入课程序号
                if courseid > len(xkid):
                    print("没有对应课程！再试一次？")
                    continue
                courseId = xkid[courseid - 1]
                c.processingData(courseId)
                if courseid == 0:
                    break
            break
        else:
            print('即将将重新登录, 请等待...')
            time.sleep(3)
