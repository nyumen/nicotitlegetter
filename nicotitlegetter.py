# -*- coding: utf-8 -*-
import requests
import time
import csv
import sys
import datetime
from xml.etree import ElementTree

mail = sys.argv[1]
password = sys.argv[2]
start_sm = int(sys.argv[3])
end_sm = int(sys.argv[4])
step = 200
wait = 3


url_login = "https://account.nicovideo.jp/api/v1/login?show_button_twitter=1&site=niconico&show_button_facebook=1&next_url=&mail_or_tel=1"
login_info = {
    'mail_tel': mail,
    'password': password
}

with requests.Session() as session:
    st = session.post(url_login, data=login_info)
#    print('login_status:'+str(st.status_code))


def get_content(session, start_pos, end_pos):

    smlist = []
    for num in range(start_pos, end_pos + 1):
        smlist.append("sm"+str(num))

    param = (",".join(smlist))

    st = session.get(
        "https://api.ce.nicovideo.jp/nicoapi/v1/video.array?v="+param)
    # print(st.text)
    #    print(st.headers)

    root = ElementTree.fromstring(st.text)
    elements = root.findall('video_info')
    video_list = {}
    for elem in elements:
        video_obj = {
            "title": elem.find('video').find('title').text,
            "user_id": int(elem.find('video').find('user_id').text),
            "deleted": int(elem.find('video').find('deleted').text),
            "length": int(elem.find('video').find('length_in_seconds').text),
            "view_count": int(elem.find('video').find('view_counter').text),
            "comment_count": int(elem.find('thread').find('num_res').text),
        }
        video_list[elem.find('video').find('id').text] = video_obj

    return video_list


# main

start_time = datetime.datetime.now()
print("開始", start_time.strftime("%H:%M:%S"))
file_name = "sm"+str(start_sm)+"-sm"+str(end_sm)+".tsv"
with open(file_name, 'x', encoding='utf-8', newline="\n") as f:
    writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    head = ['id', 'title', 'user_id', 'deleted', 'length', 'view_count', 'comment_count']
    writer.writerow(head)
    for start_pos in range(start_sm, end_sm, step):
        end_pos = start_pos + (step-1)
        if end_pos > end_sm:
            end_pos = end_sm

        time.sleep(wait)
        video_list = get_content(session, start_pos, end_pos)
        write_list = []
        for num in range(start_pos, (end_pos + 1)):
            key = "sm"+str(num)
            if key in video_list:
                data = video_list[key]
                write_data = [
                    key,
                    data['title'],
                    data['user_id'],
                    data['deleted'],
                    data['length'],
                    data['view_count'],
                    data['comment_count']
                ]
            else:
                write_data = [key, "*存在しません"]
            write_list.append(write_data)
        print("processing", str(start_pos)+"-"+str(end_pos))
        writer.writerows(write_list)

now = datetime.datetime.now()
print("終了", now.strftime("%H:%M:%S"))
totle_time = now - start_time
print("実行時間", totle_time)
