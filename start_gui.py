import tkinter
from src.gui import login


def main():
    root = tkinter.Tk()
    login_window = login.LoginWindow(None)
    root.withdraw()
    login_window.mainloop()


if __name__ == '__main__':
    main()
