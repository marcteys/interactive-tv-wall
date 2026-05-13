class App:
    def __init__(self):
        self.frame_count = 0

    def setup(self):
        pass

    def update(self):
        self.frame_count += 1

    def draw(self):
        pass

    def run(self):
        self.setup()
        self.update()
        self.draw()


if __name__ == "__main__":
    App().run()
