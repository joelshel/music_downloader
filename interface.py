#!/usr/bin/env python3

import tkinter as tk
import download as dl


class PEntry():
    def __init__(self, master, text):
        self.root = tk.Frame(master)
        self.label = tk.Label(self.root, text=text, width=9, anchor='w')
        self.entry = tk.Entry(self.root)
    
    def grid(self, **kwargs):
        self.root.grid(**kwargs, padx=10, pady=(10, 0))
        self.label.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
  

def main():
    root = tk.Tk()
    root.resizable(False, False)
    # root_tk.geometry("400x240")
    
    entry1 = PEntry(root, "username:")
    entry2 = PEntry(root, "playlist:")

    entry1.grid(row=0, column=0)
    entry2.grid(row=1, column=0)

    button = tk.Button(master=root, text="Download", command=dl.download)
    button.grid(row=3, column=0, sticky=tk.N, pady=10)

    root.mainloop()


if __name__ == '__main__':
    main()
