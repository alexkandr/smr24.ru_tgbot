from models.tables import AddressesTable, CartsTable, ImagesTable, ItemsTable, \
OrderedItemsTable, OrdersTable, UsersTable

class DBContext:
       def __init__(self):
              self.addresses = AddressesTable.AddressesTable() 
              self.carts = CartsTable.CartsTable() 
              self.images = ImagesTable.ImagesTable()
              self.items = ItemsTable.ItemsTable()
              self.ordered_items = OrderedItemsTable.OrderedItemsTable() 
              self.orders = OrdersTable.OrdersTable()
              self.tusers = UsersTable.UsersTable()