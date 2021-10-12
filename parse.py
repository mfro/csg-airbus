import re
import csv
import sys
import datetime
import dateparser

def main():
    print(f'Working with csv files: {sys.argv[1:]}')
    season_id = input("Season ID (next number in database): ")
    season_name = input("Season name (eg Winter Break 2019): ")

    match = re.search('(Spring|Fall|Thanksgiving|Winter) Break (\d{4})', season_name)

    if match:
        if match.group(1) == 'Spring':
            season_handle = 500
        if match.group(1) == 'Fall':
            season_handle = 200
        if match.group(1) == 'Thanksgiving':
            season_handle = 300
        if match.group(1) == 'Winter':
            season_handle = 400

        season_handle += (int(match.group(2)) % 100) * 1000
        print(f"Season handle: {season_handle}")
    else:
        season_handle = input("Season handle: ")

    season_charge = input("Season ticket charge: ")
    season_open = input('Season open date [today]: ')
    season_close = input('Season close date [after last trip]: ')

    sql = ''
    latest_date = None

    for file in sys.argv[1:]:
        print(f'{file}:')
        lines = []

        direction = input('Direction (eastbound | westbound): ')
        date = dateparser.parse(input('Date: ')).date()

        if direction == 'eastbound':
            capacity = input('Capacity [48]: ')
            if capacity == '': capacity = 48
            else: capacity = int(capacity)

            start = input('Reservations open [today]: ')
            if start == '': start = datetime.datetime.now()
            else: start = dateparser.parse(start)

            close = input('Reservations close [6pm day before]: ')
            if close == '':
                close = date - datetime.timedelta(days = 1)
                close = datetime.datetime(close.year, close.month, close.day, 18, 0, 0)
            else: close = dateparser.parse(close)

            print('Note: column numbers start at 0')
            number_col = int(input('Column number: trip number: '))
            block_col = int(input('Column number: vehicle block number: '))

            stops = ['bursley', 'hill', 'state', 'airport']
        else:
            print('Note: column numbers start at 0')
            number_col = int(input('Column number: trip number: '))
            stops = ['north', 'mcnamara', 'annarbor']

        schedule_cols = []
        for stop in stops:
            schedule_cols.append(int(input(f'Column number: stop {stop}: ')))

        if latest_date is None or date > latest_date:
            latest_date = date

        with open(file, 'r') as raw:
            src = csv.reader(raw)
            for row in src:
                number = row[number_col]
                block = row[block_col]
                schedule = [dateparser.parse(row[x]) for x in schedule_cols]
                if any(x is None for x in schedule):
                    continue
                for i in range(1, len(schedule)):
                    if schedule[i] < schedule[i - 1]:
                        print("invalid schedule: ", row)
                        exit(1)
                schedule = [x.time().isoformat() for x in schedule]

                times = '"' + '","'.join(schedule) + '"'

                if direction == 'eastbound':
                    sql += f'\nINSERT INTO orms_trips (seasonId, number, direction, date, capacity, blockNumber, reservationsOpen, reservationsClose, {",".join(stops)}) ' + \
                        f'VALUES ({season_id}, {number}, "eastbound", "{date}", {capacity}, {block}, "{start}", "{close}", {times});'
                else:
                    sql += f'\nINSERT INTO orms_westbound (seasonId, number, date, {",".join(stops)}) ' + \
                        f'VALUES ({season_id}, {number}, "{date}", {times});'

    if season_open == '': season_open = datetime.datetime.now()
    else: season_open = dateparser.parse(season_open)

    if season_close == '':
        season_close = latest_date + datetime.timedelta(days = 1)
        season_close = datetime.datetime(season_close.year, season_close.month, season_close.day, 12, 0, 0)
    else: season_close = dateparser.parse(season_close)

    sql = f'INSERT INTO orms_seasons (id, handle, name, ticketCharge, open, close) ' + \
          f'VALUES ({season_id}, {season_handle}, "{season_name}", {season_charge}, "{season_open}", "{season_close}");' + sql

    with open('out.sql', 'w') as out:
        out.write(sql)

main()
