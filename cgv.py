import sys
import json
import requests
import pathlib
from cinema import Cinema


class CGV(Cinema):
    def __init__(self, type):
        self.type = type
    
    def get_time_table_data(self, theater_cd, PlayYMD):
        url = "https://m.cgv.co.kr/WebAPP/Reservation/Common/ajaxTheaterScheduleList.aspx/GetTheaterScheduleList"

        payload = {
            "strRequestType": "THEATER",
            "strUserID": "",
            "strMovieGroupCd": "",
            "strMovieTypeCd": "",
            "strPlayYMD": PlayYMD,
            "strTheaterCd": theater_cd,
            "strScreenTypeCd": "",
            "strRankType": "MOVIE"
        }

        headers = {
            "Cache-Control": "no-cache",
            "Accept": "application/json",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,ko;q=0.7",
            "Content-Type": "application/json",
            "Host": "m.cgv.co.kr",
            "Origin": "https://m.cgv.co.kr",
            "Cookie": "URL_PREV_COMMON=https%253a%252f%252fm.cgv.co.kr%252fWebApp%252fReservation%252fQuickResult.aspx",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }

        result = []

        try:

            res = requests.post(url, json=payload, headers=headers)
            data = json.loads(res.content)
            data = json.loads(data['d'])

            # print(f"{json.dumps(data, ensure_ascii=False, sort_keys=False, indent=4)}")
            # store_file(data, f"schedule_{theater_cd}_{PlayYMD}.json")

            isSuccess = data['ResultCode'] == '00000'
            if isSuccess:
                tables = data['ResultSchedule']['ScheduleList']
                for table in tables:
                    result.append({
                        "movie_cd_group": table['MovieGroupCd'],
                        "movie_nm": table['MovieNmKor'],
                        "screen_cd": table['ScreenCd'],
                        "screen_nm": table['ScreenNm'],
                        "play_ymd": table['PlayYmd'],
                        "play_start_tm": table['PlayStartTm'],
                        "play_end_tm": table['PlayEndTm'],
                        "seat_remain_cnt": table['SeatRemainCnt'],
                        "seat_capacity": table['SeatCapacity'],
                        "screen_rating_cd": table['ScreenRatingCd'],
                        "allow_sale_yn": table['AllowSaleYn'],
                        "movie_pkg_yn": table['MoviePkgYn'],
                        "movie_noshow_yn": table['MovieNoshowYn'],
                        "play_start_tm_num": int(table['PlayStartTm']),
                        "movie_attr_nm": table['MovieAttrNm'],
                    })
        except:
            print("[ajaxTheaterScheduleList] Unexpected error:", sys.exc_info())

        return result


def store_file(results, filename):
    p = pathlib.Path(__file__).with_name(filename)
    with p.open('w') as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)

