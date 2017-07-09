


def get_data_from_db(data, data_symbols, start_date, end_date):
    for sym in data_symbols:
        if data is None:
            data = sym.get_data(start_date, end_date)
        else:
            data = data.combine_first(sym.get_data(start_date, end_date))

    return data