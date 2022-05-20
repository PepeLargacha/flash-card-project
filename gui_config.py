from tkinter import *
from random import choice
import pandas

BACKGROUND_COLOR = "#B1DDC6"
RIGHT_BUTTON = 'images/right.png'
WRONG_BUTTON = 'images/wrong.png'

# ---------- CANVAS ----------- #
class FlashCard(Canvas):

    def __init__(self, gui):
        super().__init__()
        self.chosen_index = None
        self.chosen_word = None
        self.translation = None
        self.parent_gui = gui
        self.front = PhotoImage(file="images/card_front.png")
        self.back = PhotoImage(file="images/card_back.png")
        self.config(width=800, height=526, background=BACKGROUND_COLOR, highlightthickness=0)
        self.card = self.create_image(405, 268, image=self.front)
        self.language = self.create_text(400, 150, text="", font=('Arial', 40, 'italic'))
        self.word = self.create_text(400, 268, text="", font=('Arial', 60, 'bold'))
        self.tkraise(self.language, self.word)

    def flip(self, data):
        self.itemconfig(self.card, image=self.back)
        self.itemconfig(self.language, text='English', fill='white')
        self.translation = data['English'][self.chosen_index]
        self.itemconfig(self.word, text=self.translation, fill='white')

    def get_new_word(self, index_list, data, language):
        try:
            self.parent_gui.after_cancel(self.parent_gui.flip_timer)
        except ValueError:
            pass
        self.itemconfig(self.language, text=language, fill='black')
        self.itemconfig(self.card, image=self.front)
        self.chosen_index = choice(index_list)
        self.chosen_word = data[language][self.chosen_index]
        self.itemconfig(self.word, text=self.chosen_word, fill='black')
        self.parent_gui.flip_timer = self.parent_gui.after(3000, lambda: self.flip(data))
        self.parent_gui.words_index.remove(self.chosen_index)


# ----------------------------- UI -------------------------------- #
class MyGui(Tk):

    def __init__(self):
        super().__init__()
        self.language = None
        self.flashcard = None
        self.data = None
        self.words_index = None
        self.flip_timer = None
        self.protocol("WM_DELETE_WINDOW", self.finalize)
        self.config(background=BACKGROUND_COLOR, padx=50, pady=50)
        self.title("Flashy")
        self.text = Label(text='Choose your Language:', background=BACKGROUND_COLOR,
                          font=('Arial', 16, 'bold'))
        self.french = Button(text='French',
                             command=lambda: (self.set_language("French"),
                                              self.initialize_language()),
                             font=('Arial', 12, 'bold'))
        self.text.grid()
        self.french.grid()

    def initialize_language(self):
        self.grab_data()
        print(len(self.words_index))
        self.text.grid_forget()
        self.french.grid_forget()
        self.flashcard = FlashCard(self)
        self.flashcard.get_new_word(self.words_index, self.data, self.language)
        self.flashcard.itemconfig(self.flashcard.language, text=self.language)
        right_image = PhotoImage(file=RIGHT_BUTTON)
        wrong_image = PhotoImage(file=WRONG_BUTTON)
        right_btn = Button(image=right_image, highlightthickness=0,
                           command=lambda: self.flashcard.get_new_word(self.words_index, self.data, self.language))
        wrong_btn = Button(image=wrong_image, highlightthickness=0,
                           command=lambda: self.flashcard.get_new_word(self.words_index, self.data, self.language))
        self.flashcard.grid(column=0, row=0, columnspan=2)
        wrong_btn.grid(column=0, row=1)
        right_btn.grid(column=1, row=1)
        self.mainloop()

    def set_language(self, language):
        self.language = language

    def grab_data(self):
        try:
            self.data = pandas.read_csv(f'data/{self.language.lower()}_words_to_learn.csv')
        except FileNotFoundError:
            self.data = pandas.read_csv(f'data/{self.language.lower()}_words.csv')
        finally:
            self.words_index = [i for i in self.data.index]

    def finalize(self):
        new_data = self.data.loc[self.words_index]
        new_data.reset_index()
        new_data.to_csv(f"data/{self.language.lower()}_words_to_learn.csv", index=False)
        self.destroy()
