from states.status_info import HotelStatus
from handlers.default_heandlers import bestdeal


def register_handlers_lowprice(dp):
    dp.register_message_handler(bestdeal.command_handler,
                                commands=['lowprice', 'highprice', 'bestdeal'], state='*')
    dp.register_message_handler(bestdeal.city_name_handler, state=HotelStatus.city)
    dp.register_callback_query_handler(bestdeal.keyboard_handler, state=HotelStatus.city)
    dp.register_callback_query_handler(bestdeal.callback_calendar, state=HotelStatus.check_in)
    dp.register_callback_query_handler(bestdeal.callback_check_out, state=HotelStatus.check_out)
    dp.register_message_handler(bestdeal.hotels_count_handler, state=HotelStatus.hotels_count)
    dp.register_message_handler(bestdeal.get_photo_handler, state=HotelStatus.get_photo)
    dp.register_message_handler(bestdeal.photo_count_handler, state=HotelStatus.photo_count)
    dp.register_message_handler(bestdeal.get_requests, state=HotelStatus.photo_count)
