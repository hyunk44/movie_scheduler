import os
import copy
import json
import pathlib
from datetime import datetime
from cinema import Cinema


######################################################################################################

# 포함할 영화 검색어
IN_MOVIE_NM_LIST = [
    "와일드 로봇",
    "조커",
    "대도시의 사랑법"
]

# 제외할 영화 검색어
EX_MOVIE_NM_LIST = [
    "하츄핑",
    # "블루 록",
    "아이엠스타",
    "빈센트",
    "명탐정",
    # "봇치",
    "정국"
    # "트랜스포머"
]

# 검색할 날짜
PLAY_YMDS = [
    "20240928",
    "20241001",
    "20241003"
]

# 상영 시작시간/종료시간
START_TM = "0800"
END_TM = "2350"

# 중간 쉬는 시간
INTERMISSION_TM = "0000"
INTERMISSION_LIMIT = 45

# 결과물 출력수
LIST_COUNT = 20

SCREEN_DATA = [
    {
        "type": "CGV",
        "code": "0013",
        "name": "용산"
    },
    {
        "type": "CGV",
        "code": "0074",
        "name": "왕십리"
    },
    {
        "type": "CGV",
        "code": "0054",
        "name": "일산"
    },
    {
        "type": "CGV",
        "code": "0310",
        "name": "파주야당"
    },
    # {
    #     "type": "CGV",
    #     "code": "0145",
    #     "name": "화정"
    # },
    # {
    #     "type": "CGV",
    #     "code": "0150",
    #     "name": "신촌아트레온"
    # },
    # {
    #     "type": "CGV",
    #     "code": "0191",
    #     "name": "홍대"
    # },
    # {
    #     "type": "CGV",
    #     "code": "0009",
    #     "name": "명동"
    # },
    {
        "type": "CGV",
        "code": "0112",
        "name": "여의도"
    },
    # {
    #     "type": "Megabox",
    #     "code": "1581",
    #     "name": "목동"
    # },
    # {
    #     "type": "Megabox",
    #     "code": "0041",
    #     "name": "현대백화점"
    # },
    # {
    #     "type": "Megabox",
    #     "code": "1351",
    #     "name": "코엑스"
    # },
]

######################################################################################################

def filter_data_for_freepass(time_table_data, ex_movie_nm_list, start_tm, end_tm):
    result = []

    for table in time_table_data:
        if (table['screen_rating_cd'] != "01"):
            continue
        if (table['allow_sale_yn'] != "Y"):
            continue
        if (table['movie_pkg_yn'] != "N"):
            continue
        if (table['movie_noshow_yn'] != "N"):
            continue
        if ("더빙" in table['movie_attr_nm']):
            continue
        if ("STAGE" in table['movie_attr_nm']):
            continue

        if start_tm:
            play_start_tm = table['play_start_tm']
            if int(play_start_tm) < int(start_tm):
                continue
        
        if end_tm:
            play_end_tm = table['play_end_tm']
            if int(play_end_tm) > int(end_tm):
                continue
        
        is_ex_movie = False
        if ex_movie_nm_list:
            movie_nm = table['movie_nm'].replace(" ", "")
            for ex_movie_nm in ex_movie_nm_list:
                ex_movie_nm = ex_movie_nm.replace(" ", "")
                if ex_movie_nm in movie_nm:
                    is_ex_movie = True
                    break
        
        if is_ex_movie:
            continue

        result.append(table)
    
    return result

def merge_by_group(time_table_data):
    result = {}

    for table in time_table_data:
        movie_cd_group = table['movie_cd_group']

        if (movie_cd_group in result):
            tables = result[movie_cd_group]
            tables.append(table)
        else:
            new_tables = []
            new_tables.append(table)
            result[movie_cd_group] = new_tables
    
    return result

def sort_by_play_start_tm(merged_schedule):
    sorted_schedule = {}
    for movie_cd_group, tables in merged_schedule.items():
        tables = sorted(tables, key=lambda x : -x['play_start_tm_num'], reverse=True)
        sorted_schedule[movie_cd_group] = tables
    
    return sorted_schedule

def recursive(sorted_schedule, intermission_tm, prev_table, assigned_list, result, depth):
    assigned_list.append(prev_table)
    depth = depth +1
    intermission_min = int(intermission_tm[:-2]) * 60 + int(intermission_tm[-2:])

    for movie_cd_group, tables in sorted_schedule.items():
        isAssigned = False
        for assigned in assigned_list:
            if movie_cd_group == assigned['movie_cd_group']:
                isAssigned = True
                break
        
        if isAssigned:
            continue

        last_play_end_tm = prev_table['play_end_tm']
        last_play_end_min = int(last_play_end_tm[:-2]) * 60 + int(last_play_end_tm[-2:])

        next = {}
        for next_table in tables:
            play_start_tm = next_table['play_start_tm']
            play_start_min = int(play_start_tm[:-2]) * 60 + int(play_start_tm[-2:])

            if (play_start_min > (last_play_end_min + intermission_min)):
                next = next_table
                recursive(sorted_schedule, intermission_tm, next, copy.deepcopy(assigned_list), result, depth)
                break

    result.append(assigned_list)

    return result

def get_combination_by_condition(screen, play_ymd, ex_movie_nm_list, in_movie_nm_list, start_tm, end_tm, intermission_tm, list_count):

    screen_cd = screen['code']
    screen_name = screen['name']
    screen_type = screen['type']

    schedule = []
    if not is_past_date(play_ymd):
        cinema = Cinema.get_cinema(screen_type)
        schedule = cinema.get_time_table_data(screen_cd, play_ymd)
        # store_file(schedule, f"schedule_{screen_cd}_{play_ymd}.json")

    filtered_schedule = filter_data_for_freepass(schedule, ex_movie_nm_list, start_tm, end_tm)
    # store_file(filtered_schedule, "filtered_schedule.json")

    merged_schedule = merge_by_group(filtered_schedule)
    # store_file(merged_schedule, "merged_schedule.json")

    sorted_schedule = sort_by_play_start_tm(merged_schedule)
    # store_file(sorted_schedule, "sorted_schedule.json")

    # read file
    # sorted_schedule = read_file("sorted_schedule.json")

    total = 0
    totla_result = []
    for movie_cd_group, tables in sorted_schedule.items():

        result = []
        for t in tables:
            # intermission (play_end_tm - play_start_tm)
            result.extend(recursive(sorted_schedule, intermission_tm, t, [], [], 0))

        # print(result)

        # must include (movie_nm)
        filtered_result = []
        if in_movie_nm_list:
            trip_in_movie_nm_list = []
            for imn in in_movie_nm_list:
                trip_in_movie_nm_list.append(imn.replace(" ", ""))

            for list in result:
                movie_nm_list = []
                for r in list:
                    movie_nm_list.append(r['movie_nm'].replace(" ", ""))

                is_all_match = True
                for timn in trip_in_movie_nm_list:
                    is_exist = False
                    for mnl in movie_nm_list:
                        if timn in mnl:
                            is_exist = True
                            break
                    if not is_exist:
                        is_all_match = False
                        break

                if is_all_match:
                    filtered_result.append(list)
                # else:
                #     print(f"필수 조건 미충족 {movie_nm_list}")
        else:
            filtered_result = result

        total += len(filtered_result)
        totla_result = totla_result + filtered_result

        # print(f"기준: [{tables[0]['movie_nm']}], 경우의 수: {len(result)}")

    print("----------------------------------------------------------------------------------------------")
    print(f"*필터 조건\n 상영관: [{screen_type}]{screen_name}\n 날짜: {play_ymd}\n 시작시간: {start_tm}\n 종료시간: {end_tm}\n 쉬는시간: {intermission_tm}\n 긴 쉬는시간 기준: {INTERMISSION_LIMIT}분\n 제외영화: {ex_movie_nm_list}\n 필수영화: {in_movie_nm_list}\n 출력항목수: {list_count}\n")
    print(f"모든 경우의 수 : {total}\n")

    sorted_totla_result = sorted(totla_result, key=len, reverse=True)
    normal_results = []
    long_intermission_results = []

    for r in sorted_totla_result[:list_count]:
        text_list = []
        assigned_text = f"[ {len(r)} ] "
        pre_end_tm = ""
        is_long_intermission = False

        for assigned in r:
            play_start_tm = assigned['play_start_tm']
            play_end_tm = assigned['play_end_tm']
            intermission_tm = ""
            if pre_end_tm:
                end_min = int(pre_end_tm[:-2]) * 60 + int(pre_end_tm[-2:])
                start_tm = int(play_start_tm[:-2]) * 60 + int(play_start_tm[-2:])
                intermission_min = start_tm - end_min
                if intermission_min > INTERMISSION_LIMIT:
                    is_long_intermission = True
                intermission_tm = f"({intermission_min}) - "
            text_list.append(f"{intermission_tm}{assigned['movie_nm']}({play_start_tm[:-2]}:{play_start_tm[-2:]}-{play_end_tm[:-2]}:{play_end_tm[-2:]})")
            pre_end_tm = play_end_tm
        
        assigned_text += " - ".join(text_list)

        if is_long_intermission:
            long_intermission_results.append(assigned_text)
        else:
            normal_results.append(assigned_text)
    
    if normal_results:
        print("------------------------------------------------------------------------------------------------")

    for normal_result in normal_results:
        print(normal_result)
    
    if long_intermission_results:
        print(f'\n--------------------------------- 긴 쉬는시간 스케줄 ---------------------------------------------')

    for long_intermission_result in long_intermission_results:
        print(long_intermission_result)
    
    print()

def is_past_date(play_ymd):
    today = datetime.now().strftime('%Y%m%d')

    if not play_ymd:
        return True
    elif play_ymd < today:
        return True
    
    return False

def store_file(results, filename):
    p = pathlib.Path(__file__).with_name(filename)
    with p.open('w') as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)


for play_ymd in PLAY_YMDS:
    for screen in SCREEN_DATA:
        get_combination_by_condition(screen, play_ymd, EX_MOVIE_NM_LIST, IN_MOVIE_NM_LIST, START_TM, END_TM, INTERMISSION_TM, LIST_COUNT)

# os.system("pause")
