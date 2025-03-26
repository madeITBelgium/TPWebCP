class Model:
    name = None
    path = None

    def list(self):
        return []
    
    def get(self, arg):
        raise NotImplementedError("Method not implemented")
    
    def create(self, arg):
        raise NotImplementedError("Method not implemented")
    
    def update(self, arg):
        raise NotImplementedError("Method not implemented")

#create NotImplemented error
class NotImplementedError(Exception):
    pass
