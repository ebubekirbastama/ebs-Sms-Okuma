import subprocess
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import csv
import json

# SMS'leri ADB komutuyla okuyarak işleyen fonksiyon
def read_sms():
    command = 'adb shell content query --uri content://sms/'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = process.communicate()
    output = output.decode().strip()

    # SMS'leri parse et
    sms_list = output.split('\n')
    sms_messages = []
    for sms in sms_list:
        sms_info = {}
        items = sms.split(', ')
        for item in items:
            if '=' in item:
                key, value = item.split('=', 1)
                sms_info[key.strip()] = value.strip()
        
        # Tarih formatlama (date ve date_sent için)
        for date_key in ['date', 'date_sent']:
            if date_key in sms_info:
                try:
                    # Unix epoch time'ı insan okunabilir formata çevir
                    timestamp = int(sms_info[date_key]) / 1000  # Milisaniyeyi saniyeye çevir
                    formatted_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    sms_info[date_key] = formatted_date
                except ValueError:
                    sms_info[date_key] = "Geçersiz Tarih"
        
        # Network type'ı formatla
        if 'network_type' in sms_info:
            sms_info['network_type'] = format_network_type(sms_info['network_type'])

        sms_messages.append(sms_info)
    return sms_messages

# Network type'ı anlamlı bir formata dönüştüren fonksiyon
def format_network_type(network_type_value):
    network_types = {
        "0": "Unknown",
        "1": "GSM (2G)",
        "2": "CDMA (2G)",
        "3": "UMTS (3G)",
        "8": "LTE (4G)",
        "13": "NR (5G)"
    }
    return network_types.get(network_type_value, "Bilinmeyen Değer")

# CSV formatında kaydetme fonksiyonu
def save_as_csv(sms_messages):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=sms_messages[0].keys())
            writer.writeheader()
            writer.writerows(sms_messages)

# JSON formatında kaydetme fonksiyonu
def save_as_json(sms_messages):
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(sms_messages, json_file, ensure_ascii=False, indent=4)

# SMS verilerini GUI'ye aktarmak için Tkinter uygulaması
def show_sms_gui():
    sms_messages = read_sms()

    # Tkinter ana pencere
    root = tk.Tk()
    root.title("SMS Okuma Uygulaması")
    root.geometry("800x400")  # Varsayılan boyut
    root.minsize(600, 300)    # Minimum boyut

    # Üst Frame (Başlık veya başka bir içerik için kullanılabilir)
    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

    # Başlık
    title_label = tk.Label(top_frame, text="Telefon SMS'lerini Görüntüleme", font=("Arial", 16, "bold"))
    title_label.pack()

    # Alt Frame (Tablo için)
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar_y = tk.Scrollbar(bottom_frame, orient=tk.VERTICAL)
    scrollbar_x = tk.Scrollbar(bottom_frame, orient=tk.HORIZONTAL)

    # DataGridView benzeri tablo
    tree = ttk.Treeview(
        bottom_frame, 
        columns=list(sms_messages[0].keys()), 
        show='headings',
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar'ları tabloya bağlama
    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Sütun başlıklarını ayarla
    for col in sms_messages[0].keys():
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor=tk.CENTER)

    # Verileri tabloya ekle
    for sms in sms_messages:
        tree.insert("", tk.END, values=list(sms.values()))

    # Dinamik olarak sütun gizleme/gösterme fonksiyonu
    def toggle_column(col):
        current_width = tree.column(col, option='width')
        if current_width == 0:
            tree.column(col, width=100, anchor=tk.CENTER)  # Geri göster
        else:
            tree.column(col, width=0, stretch=tk.NO)  # Gizle

    # Kullanıcıya sütun seçimi için checkbox'lar
    checkbox_frame = tk.Frame(root)
    checkbox_frame.pack(side=tk.BOTTOM, fill=tk.X)

    column_vars = {}
    for col in sms_messages[0].keys():
        var = tk.BooleanVar(value=True)  # Varsayılan olarak tüm sütunlar açık
        column_vars[col] = var
        checkbox = tk.Checkbutton(
            checkbox_frame, 
            text=col, 
            variable=var,
            command=lambda col=col: toggle_column(col)
        )
        checkbox.pack(side=tk.LEFT)

    # CSV ve JSON dışa aktarma butonları
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    csv_button = tk.Button(button_frame, text="CSV Olarak Kaydet", command=lambda: save_as_csv(sms_messages))
    csv_button.pack(side=tk.LEFT, padx=5)

    json_button = tk.Button(button_frame, text="JSON Olarak Kaydet", command=lambda: save_as_json(sms_messages))
    json_button.pack(side=tk.LEFT, padx=5)

    root.mainloop()

# GUI'yi çalıştır
if __name__ == "__main__":
    show_sms_gui()
