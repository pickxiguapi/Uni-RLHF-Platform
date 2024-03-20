

class BaseOfflineDataset(object):
    def __init__(self):
        pass
        
    def load_offline_dataset(self):
        raise NotImplementedError("load_offline_dataset method must be implemented in subclasses.")
        
    def get_episode_boundaries(self):
        raise NotImplementedError("get_episode_boundaries method must be implemented in subclasses.")
    
    def sample(self):
        raise NotImplementedError("sample method must be implemented in subclasses.")
        
    def visualize(self):
        raise NotImplementedError("visualize method must be implemented in subclasses.")
        
    def query(self):
        raise NotImplementedError("query method must be implemented in subclasses.")