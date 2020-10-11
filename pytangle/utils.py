# Copyright (C) 2020 Mattia Samory

def remove_null_values_from_dict(params):
    return dict(filter(lambda x: x[1] is not None, params.items()))