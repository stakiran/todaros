# encoding: utf-8

import copy
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

    dow_longnames = ['monday',"tuesday", "wednesday", "thursday","friday","saturday","sunday"]
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

# Routine Group という単語を定義する
# - ('@1', '@1.md') のようなタプル
# - (prefix, filename)
#   - filename には n 個のタスク行が書かれている
#   - prefix は、各タスク行の先頭に付与する補足文字列

def create_routinegroups(filenames):
    routinegroups = []
    rgs = routinegroups

    for filename in filenames:
        if filename.startswith('@1'):
            rgs.append(('@1', filename))
            continue
        if filename.startswith('@2'):
            rgs.append(('@2', filename))
            continue
        if filename.startswith('@3'):
            rgs.append(('@3', filename))
            continue
        if filename.endswith('day.md'):
            rgs.append(('[Dow]', filename))
            continue
        rgs.append(('[Day]', filename))

    return rgs

def file2list_from_routinegroups(routinegroups):
    ''' @params routinegroups routinegroupのリスト '''

    result_outlines = []

    for routinegroup in routinegroups:
        prefix, filename = routinegroup
        outlines = file2list(filename)

        outlines = [line for line in outlines if len(line.strip())!=0]

        # prefix だと次の reconstruction で上手くいかない
        # こうしたいのに
        #   1 @1 毎日やりたいタスク1
        #   1 @1 毎日やりたいタスク2
        # こうなってしまう、
        #   @1 1 毎日やりたいタスク1
        #   @1 1 毎日やりたいタスク2
        #
        # 前者の実装は文字列操作がしんどいので、以下のようにする
        #   1 毎日やりたいタスク1 @1
        #   1 毎日やりたいタスク2 @1
        suffix = prefix
        #outlines = ['{} {}'.format(prefix, line) for line in outlines]
        outlines = ['{} {}'.format(line, suffix) for line in outlines]

        result_outlines.extend(outlines)

    return result_outlines

def reconstruction_tasklines_with_extract_merge(lines):
    # extract and merge
    # 指定観点で抽出(extact)した部分リストをつくったあと、
    # それらを指定順序で併合(merge)することで
    # 意図した並びのリストをつくる手法.

    outlines = []

    extractee = copy.deepcopy(lines)
    prefix_extracters = [
        '0 ',
        '1 ',
        '2 ',
        '3 ',
        '4 ',
        '5 ',
        '6 ',
        '7 ',
        '8 ',
        '9 ',
    ]

    for prefix_extracter in prefix_extracters:
        extracted_lines = []
        for line in extractee:
            not_included = not line.startswith(prefix_extracter)
            if not_included:
                continue
            extracted_lines.append(line)

        outlines.extend(extracted_lines)

        for extracted_line in extracted_lines:
            extractee.remove(extracted_line)

    # 最後に「抽出されなかった行たち」を merge する必要がある。
    # これを行いたいがために、上記処理では extractee を破壊的に remove していっている。
    not_extracted_lines = extractee
    outlines.extend(not_extracted_lines)

    return outlines

def ________arguments________():
    pass

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('--debug', default=False, action='store_true',
        help='debug print.')

    parser.add_argument('--overview', default=False, action='store_true',
        help='Generate overview.md.')

    args = parser.parse_args()
    return args

def dp(msg):
    if args.debug:
        print(msg)

def generate_overview(basedir, outname, maybe_mergee_filenames):
    mergee_filenames = []
    outlines = []

    # ルーチンを定義してない無関係ファイルを除く。
    # 良いやり方浮かばないので、todarosが扱っているファイル名が存在してるかを愚直に調べていく。
    # これには意図した順番で append したいという意図もある。
    for i in range(31):
        day = i+1
        dayfilename = '{}.md'.format(day)
        notfound = not dayfilename in maybe_mergee_filenames
        if notfound:
            continue
        mergee_filenames.append(dayfilename)
    for routinefilename in ['@1.md','@2_slot1.md','@2_slot2.md','@3_slot1.md','@3_slot2.md','@3_slot3.md']:
        notfound = not routinefilename in maybe_mergee_filenames
        if notfound:
            continue
        mergee_filenames.append(routinefilename)
    # 作者の好みで月曜始まり
    for dowfilename in ['monday.md','tuesday.md','wednesday.md','thursday.md','friday.md','saturday.md','sunday.md']:
        notfound = not dowfilename in maybe_mergee_filenames
        if notfound:
            continue
        mergee_filenames.append(dowfilename)

    for mergee_filename in mergee_filenames:
        mergee_fullpath = os.path.join(basedir, mergee_filename)
        mergee_content_lines = file2list(mergee_fullpath)

        outlines.append('# {}'.format(mergee_filename))
        outlines.extend(mergee_content_lines)

        blankline_for_readability = ''
        outlines.append(blankline_for_readability)

    outfullpath = os.path.join(basedir, outname)
    list2file(outfullpath, outlines)

def ________main________():
    pass

args = parse_arguments()

MYFULLPATH = os.path.abspath(sys.argv[0])
MYDIR = os.path.dirname(MYFULLPATH)

OUTNAME = 'daily.md'
OUT_FULLPATH = os.path.join(MYDIR, OUTNAME)

all_filenames = get_markdown_filenames_only_currentlevel(MYDIR)
dp(all_filenames)

if args.overview:
    routinegroups = create_routinegroups(all_filenames)

    basedir = MYDIR
    outname = 'overview.md'
    mergee_filenames = all_filenames
    generate_overview(basedir, outname, mergee_filenames)
    exit(0)

loadee_filenames = pickup_corresponded_filenames(all_filenames)
dp(loadee_filenames)

routinegroups = create_routinegroups(loadee_filenames)
dp(routinegroups)

tasklines = file2list_from_routinegroups(routinegroups)

outlines = reconstruction_tasklines_with_extract_merge(tasklines)
list2file(OUT_FULLPATH, outlines)
