class Cinema():

    def __init__(self, type):
        self.type = type

    def get_time_table_data(self, theater_cd, PlayYMD):
        print('get_time_table_data')

    @staticmethod
    def get_cinema(type):
        if type == 'CGV':
            from cgv import CGV
            return CGV(type)
        elif type == 'Megabox':
            from megabox import Megabox
            return Megabox(type)

        return