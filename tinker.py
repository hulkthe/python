from tkinter import Tk, Label, Button

class MyFirstGui:
	def __init__(self, master):
		self.master = master
		master.title("GUI sencilla")

		self.label = Label(master, text="Primer GUI")
		self.label.pack()

		self.greet_button = Button(master, text="Saludos", command=self.greet)
		self.greet_button.pack()

		self.close_button = Button(master, text="Cerrar", command = master.quit)
		self.close_button.pack()

	def greet(self):
			print("Saludos")

root = Tk()
my_gui = MyFirstGui(root)
root.mainloop()