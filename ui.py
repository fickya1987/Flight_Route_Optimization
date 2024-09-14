import tkinter as tk
from tkinter import ttk
import pandas as pd

class AirportSearchApp:
    def __init__(self, root, csv_file):
        self.root = root
        self.root.title("Airport Search")

        self.df = pd.read_csv(csv_file)
        self.iata_index = {row['IATA']: row['Airport_Name'] for idx, row in self.df.iterrows()}
        self.name_index = {row['Airport_Name'].lower(): row['IATA'] for idx, row in self.df.iterrows()}
        self.trie = self.build_trie()

        self.create_widgets()

    def build_trie(self):
        trie = {}
        for _, row in self.df.iterrows():
            node = trie
            for char in row['Airport_Name'].lower():
                node = node.setdefault(char, {})
            node['_end_'] = row['Airport_Name']
        return trie

    def search_iata(self, iata):
        return self.iata_index.get(iata.upper(), "Airport not found")

    def search_name(self, prefix):
        node = self.trie
        for char in prefix.lower():
            if char not in node:
                return []
            node = node[char]
        return self.find_airports(node)

    def find_airports(self, node, prefix='', results=None):
        if results is None:
            results = []
        if '_end_' in node:
            results.append(node['_end_'])
        for char, next_node in node.items():
            if char != '_end_':
                self.find_airports(next_node, prefix + char, results)
        return results

    def autocomplete(self, prefix, max_results=5):
        results = self.search_name(prefix)
        return results[:max_results]

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Enter Airport Name or IATA Code:")
        self.label.pack(pady=10)

        self.entry = ttk.Entry(self.root, width=50)
        self.entry.pack(pady=10)
        self.entry.bind('<KeyRelease>', self.on_key_release)

        self.listbox = tk.Listbox(self.root, width=50, height=10)
        self.listbox.pack(pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack(pady=10)

    def on_key_release(self, event):
        input_text = self.entry.get()
        if len(input_text) == 3:
            # Likely an IATA code
            airport_name = self.search_iata(input_text)
            self.result_label.config(text=f"IATA Code: {input_text} -> Airport: {airport_name}")
            self.listbox.delete(0, tk.END)
        else:
            # Autocomplete based on airport name
            suggestions = self.autocomplete(input_text)
            self.listbox.delete(0, tk.END)
            for suggestion in suggestions:
                self.listbox.insert(tk.END, f"{suggestion} ({self.name_index[suggestion.lower()]})")

    def on_select(self, event):
        selected_airport = self.listbox.get(self.listbox.curselection())
        self.result_label.config(text=f"Selected Airport: {selected_airport}")

def main():
    root = tk.Tk()
    app = AirportSearchApp(root, 'airport.csv')
    root.mainloop()

if __name__ == "__main__":
    main()
