class GlobalState:
    def __init__(self):
        self.state = {
            "question": None,
            "plan": None,
            "research": None,
            "draft": None,
            "evaluation": None
        }
    
    def update(self, key: str, value: any) -> None:
        """Updates a value in the global state."""
        if key in self.state:
            self.state[key] = value
        else:
            raise KeyError(f"Key {key} not found in state.")
    
    def get(self, key: str) -> any:
        """Retrieves a value from the global state."""
        return self.state.get(key)
    
    def show(self) -> dict:
        """Returns the entire state dictionary."""
        return self.state

# Singleton instance of the state
state = GlobalState()
