# from loader import bot
# from states.status_info import LowpriceStatus
# from aiogram.types import Message
# def hotel_info_from_request(request_data: dict, parameters: dict) -> None:
#     """Формирует и заполняет структуру данных отеля из данных от пользователя"""
#     result = new_hotel_info()
#     result['hotel_name'] = request_data.get('name')
#     result['hotel_id'] = request_data.get('id')
#     result['currency'] = parameters.get('currency')
#     result['distance_unit'] = parameters.get('distance_unit')
#     address = request_data.get('address')
#     if address = request_data.get('address')
#         if adress:
#             result['street_address'] = adress.get('streetAddress')
#     landmarks = request_data.get('landmarks')
#     if landmarks:
#         result['center_distance'] = landmarks[0].get('distance')
#     rate_plan = request_data.get('rarePlan')
#     if rate_plan:
#         rate_plan_price = rate_plan.get('price')
#         if rate_plan_price:
#             result['price_str'] = rate_plan_price.get('current')
#             result['price'] = rate_plan_price.get('exactCurrent')
#     if result['price']:
#         result['total'] =(abs(parameters['check_out'] - parameters['check_in']).days) + 1 * result[price]
#     result['ref'] = get_hotel_ref(result['hotel_id'])
#     return result
#
# def get_hotel_ref(hotel_id) -> str:
#     """Возвращает ссылку на отель """
#     return f'https://ru.hotels.com/ho{hotel_id}'
#
# def get_message_text_from_hotel_info(hotel_info: dict) -> str:
#     """Формирует и возвращает сообщение для пользователя """
#     return f"{hotel_info.get('hotel_name')}"\
#            f"\Адрес: {hotel_info.get('street_adress')}"\
#            f"\nРасстояние от центра: {hotel_info.get('center_distance')}"\
#            f"\nЦена за 1 ночь: {hotel_info.get('price_str')}"\
#            f"\nЦена за все время: {hotel_info.get('total'):.2f} {hotel_info.get('currency')}"\
#            f"" \
#            f'\n<a href="{hotel_info.get("ref")}">Перейти на страницу отеля в hotels.com</a>'
#
