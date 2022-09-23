from aiogram.dispatcher.filters.state import State, StatesGroup


class BestdealStatus(StatesGroup):
    city = State()
    check_in = State()
    check_out = State()
    min_price = State()
    max_price = State()
    min_distance_center = State()
    max_distance_center = State()
    hotels_count = State()
    get_photo = State()
    photo_count = State()
    executing_request = State()


class LowpriceStatus(StatesGroup):
    city = State()
    check_in = State()
    check_out = State()
    min_price = State()
    max_price = State()
    hotels_count = State()
    get_photo = State()
    photo_count = State()
    executing_request = State()


class HighpriceStatus(StatesGroup):
    city = State()
    check_in = State()
    check_out = State()
    min_price = State()
    max_price = State()
    hotels_count = State()
    get_photo = State()
    photo_count = State()
    executing_request = State()


# MAX_HOTELS = 25
# MAX_PHOTO = 5
