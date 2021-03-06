import npyscreen

class MyTestApp(npyscreen.NPSAppManaged):
    def on_start(self):
        self.add_form_class("MAIN", MainForm)

class MainForm(npyscreen.FileSelector):
    pass

def main():
    TA = MyTestApp()
    TA.run()

def test_function(scr):
    t = npyscreen.selectFile('~/',)
    npyscreen.notify_confirm(title='Selected File', message=t)
if __name__ == '__main__':
    #main()
    print(npyscreen.wrapper(test_function))
