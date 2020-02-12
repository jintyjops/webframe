"""A module for easier creation of models, especially in testing."""

def factory(model, params={}):
    """Returns a model."""
    params = {**Factory.registered[model](), **params}
    return model(**params)


class Factory:

    registered = {}

    def __init__(self, model):
        self.model = model

    def __call__(self, func):
        Factory.registered[self.model] = func
        return func
