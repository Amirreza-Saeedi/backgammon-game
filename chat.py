import tkinter as tk
from tkinter import scrolledtext


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat")

        # جلوگیری از تغییر اندازه پنجره
        self.root.resizable(False, False)

        # بخش نمایش پیام‌ها
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # فیلد ورودی پیام
        self.message_entry = tk.Entry(root, width=40)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)
        self.message_entry.bind("<Return>", self.send_message)

        # دکمه ارسال پیام
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

    def send_message(self, sender='You', event=None):
        # دریافت متن پیام از فیلد ورودی
        message = self.message_entry.get().strip()
        if message:
            # نمایش پیام در بخش نمایش پیام‌ها
            self.chat_display.configure(state='normal')
            self.chat_display.insert(tk.END, f"{sender}: {message}\n")
            self.chat_display.see(tk.END)  # اسکرول به پایین
            self.chat_display.configure(state='disabled')

            # پاک کردن فیلد ورودی پیام
            self.message_entry.delete(0, tk.END)

    def start():
        '''
            main
        '''
        root = tk.Tk()
        app = ChatApp(root)
        root.mainloop()
