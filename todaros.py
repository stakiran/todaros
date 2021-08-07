# encoding: utf-8

import datetime
import glob
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

def get_filename(path):
    return os.path.basename(path)

def get_basename(path):
    return os.path.splitext(get_filename(path))[0]

def get_markdown_filenames_only_currentlevel(fullpath_of_directory):
    query = '{}/*.md'.format(fullpath_of_directory)
    fullpaths = glob.glob(query, recursive=False)

    filenames = []
    for fullpath in fullpaths:
        filename = get_filename(fullpath)
        filenames.append(filename)
    return filenames

def get_today_datetimeobj():
    return datetime.datetime.today()

def get_today_day():
    dtobj = get_today_datetimeobj()
    return dtobj.day

def get_today_dow_longname():
    dtobj = get_today_datetimeobj()
    dow_index = dtobj.weekday()

    dow_longnames = ['monday',"tuesday", "wednesday", "thursday","friday","saturday","sunay"]
    return dow_longnames[dow_index]

def _________func________():
    pass

def pickup_corresponded_filenames(filenames):
    today_day = get_today_day()
    today_dow_longname = get_today_dow_longname()

    per2_table = ['slot1', 'slot2']
    mod2 = today_day % 2
    target_basename_of_per2 = '@2_{}'.format(per2_table[mod2])

    per3_table = ['slot1', 'slot2', 'slot3']
    mod3 = today_day % 3
    target_basename_of_per3 = '@3_{}'.format(per3_table[mod3])

    outnames = []
    for filename in filenames:
        basename = get_basename(filename)
        b = basename

        if b == '@1':
            outnames.append(filename)
            continue

        if b == target_basename_of_per2:
            outnames.append(filename)
            continue

        if b == target_basename_of_per3:
            outnames.append(filename)
            continue

        if b==today_dow_longname:
            outnames.append(filename)
            continue
        
        if b.isnumeric() and today_day==int(b):
            day = b
            outnames.append(filename)
            continue

    return outnames

def file2list_from_filenames(filenames, ignoring_prefix):
    '''
    [ignoring_prefix]
    - これに合致するファイル名は読み込まない
    - 代わりに, ファイル名をそのまま追加する

    もっぱら区切り文字列用途.
    区切り入れるタイミングが sort_and_delimiterize_better() しかないので,
    ここでは（その時に入れられた）区切りを消さないようお膳立てする必要がある. '''

    result_outlines = []
    for filename in filenames:
        if filename.startswith(ignoring_prefix):
            result_outlines.append(filename)
            continue
        outlines = file2list(filename)
        result_outlines.extend(outlines)
    return result_outlines

def sort_and_delimiterize_better(filenames):
    # ソートする.
    # 一番自然な以下の順(出現頻度の多い順)にする.
    # 1
    #   @1
    #   @2 系
    #   @3 系
    # 2
    #   DOW 系
    # 3
    #   day 系

    # 境界がわかりづらいのでタイトルと空行も入れる.

    order1_per1 = []
    order1_per2 = []
    order1_per3 = []
    order2 = []
    order3 = []

    for filename in filenames:
        if filename.startswith('@1'):
            order1_per1.append(filename)
            continue
        if filename.startswith('@2'):
            order1_per2.append(filename)
            continue
        if filename.startswith('@3'):
            order1_per3.append(filename)
            continue

        if filename.endswith('day.md'):
            order2.append(filename)
            continue

        order3.append(filename)

    outlines = []
    outlines.append('---- @1 ----')
    outlines.extend(order1_per1)
    outlines.append('---- @2 ----')
    outlines.extend(order1_per2)
    outlines.append('---- @3 ----')
    outlines.extend(order1_per3)
    outlines.append('---- DOW ----')
    outlines.extend(order2)
    outlines.append('---- Day ----')
    outlines.extend(order3)

    return outlines

MYFULLPATH = os.path.abspath(sys.argv[0])
MYDIR = os.path.dirname(MYFULLPATH)

OUTNAME = 'daily.md'
OUT_FULLPATH = os.path.join(MYDIR, OUTNAME)

all_filenames = get_markdown_filenames_only_currentlevel(MYDIR)
print(all_filenames)

loadee_filenames = pickup_corresponded_filenames(all_filenames)
print(loadee_filenames)

loadee_filenames = sort_and_delimiterize_better(loadee_filenames)
print(loadee_filenames)

outlines = file2list_from_filenames(loadee_filenames, ignoring_prefix='-')
list2file(OUT_FULLPATH, outlines)
