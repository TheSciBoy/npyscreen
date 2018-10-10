#!/bin/env python
import npyscreen

class MainFm(npyscreen.Form):
    def create(self):
        self.mb = self.add(npyscreen.MonthBox,
                    use_datetime = True)


class TestApp(npyscreen.NPSAppManaged):
    def on_start(self):
        self.add_form("MAIN", MainFm)


if __name__ == "__main__":
    A = TestApp()
    A.run()
