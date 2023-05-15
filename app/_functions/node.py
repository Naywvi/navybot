class node:
  def __init__(self, data):
    self.data = data
    self.next_node = None

class chained_list:
  def __init__(self, data):
    self.first_node = node(data)
    self.last_node = self.first_node
    self.size = 1

  def __str__(self):
    txt = str(self.first_node.data)

    current_node = self.first_node
    while current_node.next_node != None:
      current_node = current_node.next_node
      txt += "-"+str(current_node.data)
    return txt

  def insert_first(self, data):
    N = self.first_node
    self.first_node = node(data)
    self.first_node.next_node = N
    self.size += 1

  def get_size(self):
    return self.size

  def append(self,data):
    new_last_node = node(data)
    self.last_node.next_node = new_last_node
    self.last_node = new_last_node
    self.size += 1