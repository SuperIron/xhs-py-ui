import gradio as gr
from xhs import XhsClient
from time import sleep
import pandas as pd
import time
import os


# 45 个为一轮，每轮间隔默认 3 分钟
ROUND_COUNT = 45


def xhs_to_excel(cookie, keyword, max_count, handle_delay=2, round_delay=180):
    xhs_client = XhsClient(cookie)

    notes = []
    page = 1

    while True:
        data = xhs_client.get_note_by_keyword(keyword, page=page)
        has_more = data.get('has_more')
        print("has_more: %s" % has_more)
        if (not has_more) or len(notes) >= max_count:
            break
        for item in data.get('items'):
            id = item.get('id')
            note_card = item.get('note_card')
            display_title = note_card.get('display_title')
            note_info = xhs_client.get_note_by_id(id)
            desc = note_info.get('desc')
            interact_info = note_info.get('interact_info')
            timestamp = note_info.get('time')
            notes.append({
                'url': 'https://www.xiaohongshu.com/explore/' + id,
                'display_title': display_title,
                'desc': desc,
                'collected_count': interact_info.get('collected_count'),
                "liked_count": interact_info.get("liked_count"),
                'time': time.strftime('%Y-%m-%d', time.localtime(timestamp / 1000))
            })
            cur_time = time.strftime(
                '%H:%M:%S', time.localtime(time.time()))
            print("notes: %s/%s [%s]" % (len(notes), int(max_count), cur_time))
            if len(notes) % ROUND_COUNT == 0:
                print("round_delay: %s" % round_delay)
                sleep(round_delay)
            else:
                sleep(handle_delay)
            if len(notes) >= max_count:
                break
        page += 1

    df = pd.DataFrame(notes)
    dir = os.path.dirname(os.path.abspath(__file__))
    xlsx = dir + '/notes'
    if not os.path.exists(xlsx):
        os.makedirs(xlsx)

    df.to_excel('%s/notes.%s.xlsx' %
                (xlsx, time.strftime('%Y%m%d.%H%M%S', time.localtime(time.time()))), index=False)
    print('notes to excel done!\n')


def greet(cookie, keyword, max_count, handle_delay, round_delay):
    xhs_to_excel(cookie, keyword, max_count, handle_delay, round_delay)


if __name__ == '__main__':
    cookie = gr.Textbox(label="Cookie")
    keyword = gr.Textbox(label="搜索关键词")
    max_count = gr.Number(label="爬虫数量")
    handle_delay = gr.Number(label="操作时间间隔，单位秒", value=2)
    round_delay = gr.Number(label="每轮时间间隔，单位秒", value=180)

    app = gr.Interface(
        fn=greet,
        inputs=[cookie, keyword, max_count, handle_delay, round_delay],
        outputs=[],
        title='Xhs爬虫',
    )
    app.launch()
