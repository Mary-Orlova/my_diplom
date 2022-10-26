from aiogram.dispatcher.filters.state import State, StatesGroup


class HotelStatus(StatesGroup):
    order = State()
    city_name = State()
    city = State()
    check_in = State()
    check_out = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    hotels_count = State()
    get_photo = State()
    photo_count = State()


# MAX_HOTELS = 25
# MAX_PHOTO = 5
