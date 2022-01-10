# encoding: utf-8

import datetime
import os
import sys

def file2list(filepath):
    ret = []
    with open(filepath, encoding='utf8', mode='r') as f:
        ret = [line.rstrip('\n') for line in f.readlines()]
    return ret

def list2file(filepath, ls):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.writelines(['{:}\n'.format(line) for line in ls] )

def get_today_datetimeobj():
    return datetime.datetime.today()

def get_day(dtobj):
    return dtobj.day

def get_dow(dtobj):
    dow_index = dtobj.weekday()
    dow_shortnames = ['mon',"tue", "wed", "thu", "fri", "sat", "sun"]
    return dow_shortnames[dow_index]

# [タスク]
# task1 @mon @fri @1 @10
#
# [Element]
# task1 @mon @fri @1 @10
# ^^^^^ ^^^^ ^^^^ ^^ ^^^
#
# [頻度(frequency)]
# @m
# @h
# @k
# @mon-sat
# @1-31
# @ss1, @ss2, @sss1, @sss2, @sss3
class Task:
    def __init__(self, line):
        self._taskname = ''
        self._freqs = []

        self._parse(line)

    def _parse(self, line):
        elements = line.split(' ')
        for element in elements:
            self._parse_element(element)

    def _parse_element(self, element):
        is_freq = element[0]=='@'
        if is_freq:
            self._parse_as_freq(element)
            return
        self._parse_as_taskname(element)

    def _parse_as_freq(self, element):
        self._freqs.append(element)

    def _parse_as_taskname(self, element):
        is_first = len(self._taskname)==0
        if is_first:
            self._taskname = element
            return
        newname = '{} {}'.format(self._taskname, element)
        self._taskname = newname

    def is_delimitor(self):
        # 頻度がない場合は区切りとみなす。
        is_empty_taskname = len(self._taskname)==0
        is_empty_freq = len(self._freqs)==0
        if is_empty_freq and not is_empty_taskname:
            return True
        return False

    def is_stealth_delimitor(self):
        # 頻度だけがある場合はステルス区切りとみなす。
        #
        # 例
        # @sun
        # @30
        #
        # ステルス区切りとは、入力ファイル上では区切りとして書くが
        # 出力ファイル上では表示しないもの。
        is_empty_taskname = len(self._taskname)==0
        is_empty_freq = len(self._freqs)==0
        if not is_empty_freq and is_empty_taskname:
            return True
        return False

    def is_today_task(self):
        # 日付オブジェクト毎回つくるの行儀悪いけど
        # 高々数十のタスクだし、処理もほぼ一瞬だし
        # 問題ないよね！
        todaydt = get_today_datetimeobj()

        return is_today_freq(todaydt, self._freqs)

    @property
    def displaytext(self):
        if self.is_delimitor():
            # 区切りは空行でいい
            return ''
        return self._taskname

    def __str__(self):
        return '{}: {}'.format(self._taskname, self._freqs)

def line2task(line):
    task = Task(line)
    return task

def is_today_freq(today_dtobj, freqs):
    '''
    @today_dtobj テストしやすいよう日付オブジェクトは外から与えさせる
    '''
    day = get_day(today_dtobj)
    dow = get_dow(today_dtobj)

    for freq in freqs:
        # @13
        #  ^^ value
        v = freq[1:]

        is_kyujitsu = dow=='sat' or dow=='sun'
        is_heijitsu = not is_kyujitsu

        if freq=='@m':
            return True

        if freq=='@h' and is_heijitsu:
            return True

        if freq=='@k' and is_kyujitsu:
            return True

        if v==dow:
            return True

        if v.isnumeric() and day==int(v):
            return True

        is_ss1 = day%2==1
        is_ss2 = day%2==0
        is_sss1 = day%3==1
        is_sss2 = day%3==2
        is_sss3 = day%3==0
        if v=='ss1' and is_ss1:
            return True
        if v=='ss2' and is_ss2:
            return True
        if v=='sss1' and is_sss1:
            return True
        if v=='sss2' and is_sss2:
            return True
        if v=='sss3' and is_sss3:
            return True

    return False

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('--debug', default=False, action='store_true',
        help='Enable debug print. No output generation.')

    parser.add_argument('-i', '--input', default='tasks.md',
        help='A file contained task lines.')

    parser.add_argument('-o', '--output', default='daily.md',
        help='A file of daily tasks output target.')

    args = parser.parse_args()
    return args

def ________main________():
    pass

if __name__=='__main__':
    args = parse_arguments()

    MYFULLPATH = os.path.abspath(sys.argv[0])
    MYDIR = os.path.dirname(MYFULLPATH)

    in_fullpath = os.path.join(MYDIR, args.input)
    out_fullpath = os.path.join(MYDIR, args.output)

    lines = file2list(in_fullpath)
    tasks = []
    for line in lines:
        is_blankline = len(line.strip())==0
        if is_blankline:
            continue

        is_sectionline = line[0]=='#'
        if is_sectionline:
            continue

        task = line2task(line)
        tasks.append(task)

    today_tasks = []
    for task in tasks:
        if task.is_delimitor():
            today_tasks.append(task)
            continue
        if task.is_today_task():
            today_tasks.append(task)
            continue

    if args.debug:
        for task in today_tasks:
            if task.is_stealth_delimitor():
                continue
            print(task.displaytext)
        sys.exit(0)

    outlines = []
    for task in today_tasks:
        outline = task.displaytext
        outlines.append(outline)
    list2file(out_fullpath, outlines)
