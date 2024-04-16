from aiogram.fsm.state import StatesGroup, State

class AddressState(StatesGroup):
    delete_address = State()
    choose_city = State()
    choose_street = State()
    choose_house = State()
    choose_building  = State()
    choose_office = State()
    choose_index = State()

class PurchaseState(StatesGroup):
    ChooseAddress = State()
    Accept = State()


class GiveIdState(StatesGroup):
    Recieve_image = State()

class SearchState(StatesGroup):
    Search = State()

class CatalogState(StatesGroup):
    chooseNomenklature = State()
