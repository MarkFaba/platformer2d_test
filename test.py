class OnAndOff:
    def __init__(self):
        self.state = False
        self.previous_state = False

    def update(self):
        if self.state != self.previous_state:
            print("State changed!")
            self.previous_state = self.state


on_and_off = OnAndOff()
on_and_off.state = True
on_and_off.update()
print(on_and_off.state)
print(on_and_off.previous_state)