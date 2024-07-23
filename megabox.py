import sys
import json
import requests
from cinema import Cinema


class Megabox(Cinema):
    def __init__(self, type):
        self.type = type

    def get_time_table_data(self, theater_cd, PlayYMD):

        url = "https://www.megabox.co.kr/on/oh/ohc/Brch/schedulePage.do"

        payload = {
            "masterType": "brch",
            "detailType": "area",
            "brchNo": theater_cd,
            "firstAt": "N",
            "brchNo1": theater_cd,
            # "crtDe": "20230816",
            "playDe": PlayYMD
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        result = []

        try:

            res = requests.post(url, json=payload, headers=headers)
            data = json.loads(res.content)

            # print(f"{json.dumps(data, ensure_ascii=False, sort_keys=False, indent=4)}")

            isSuccess = data['statCd'] == 0
            if isSuccess:
                tables = data['megaMap']['movieFormList']
                for table in tables:
                    play_start_tm_num = table['playStartTime'].replace(":", "")
                    play_end_tm = table['playEndTime'].replace(":", "")

                    screen_rating_cd = "00"
                    if table['cttsTyDivCd'] == "MVCT01": #일반콘텐트
                        screen_rating_cd = "01"

                    allow_sale_yn = "N"
                    if table['movieStatCd'] == "MSC01": #상영중
                        allow_sale_yn = "Y"

                    result.append({
                        "movie_cd_group": table['rpstMovieNo'],
                        "movie_nm": table['rpstMovieNm'],
                        "screen_cd": table['theabNo'],
                        "screen_nm": table['theabExpoNm'],
                        "play_ymd": table['playDe'],
                        "play_start_tm": play_start_tm_num,
                        "play_end_tm": play_end_tm,
                        "seat_remain_cnt": table['restSeatCnt'],
                        "seat_capacity": table['totSeatCnt'],
                        "screen_rating_cd": screen_rating_cd,
                        "allow_sale_yn": allow_sale_yn,
                        "movie_pkg_yn": "N",
                        "movie_noshow_yn": "N",
                        "play_start_tm_num": int(play_start_tm_num),
                        "movie_attr_nm": table['playKindNm'],
                    })
        except:
            print("[schedulePage] Unexpected error:", sys.exc_info())

        return result


