from aiogram.fsm.state import State, StatesGroup


# все необходимые стейты для фсм
class Admin(StatesGroup):
    mailing_state = State()
    mailing_text = State()
    mailing_text_only = State()
    ask = State()
    confirm_yes = State()
    confirm_no = State()
    position_name = State()
    position_photo = State()
    description = State()
    calorie_content = State()
    ingredients = State()
    allergens = State()
    cost = State()
    number_position = State()
    geo = State()
    geo2 = State()
    time_data = State()
    number = State()
    comment = State()
    payment = State()
