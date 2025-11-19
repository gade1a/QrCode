import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import qrcode
from qrcode.image.pil import PilImage

def gerar_qrcode():
    dados = entrada.get()
    if not dados.strip():
        messagebox.showwarning("Aviso", "Por favor, insira algum texto ou URL!")
        return

    # Escolher cores
    cor_qr = cor_qrcode.get() if cor_qrcode.get() else "black"
    cor_bg = cor_fundo.get() if cor_fundo.get() else "white"

    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(dados)
    qr.make(fit=True)

    img = qr.make_image(fill_color=cor_qr, back_color=cor_bg).convert("RGB")

    # Adicionar logo
    if caminho_logo.get():
        try:
            logo = Image.open(caminho_logo.get())
            logo = logo.resize((50, 50))  # Ajusta tamanho do logo
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível adicionar o logo: {e}")

    # Salvar arquivo
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if caminho_arquivo:
        img.save(caminho_arquivo)
        messagebox.showinfo("Sucesso", f"QR Code salvo em:\n{caminho_arquivo}")

    # Exibir na interface
    img_tk = ImageTk.PhotoImage(img)
    label_imagem.config(image=img_tk)
    label_imagem.image = img_tk

def escolher_cor_qr():
    cor = colorchooser.askcolor()[1]
    if cor:
        cor_qrcode.set(cor)

def escolher_cor_bg():
    cor = colorchooser.askcolor()[1]
    if cor:
        cor_fundo.set(cor)

def escolher_logo():
    caminho = filedialog.askopenfilename(filetypes=[("Image files", ".png;.jpg;*.jpeg")])
    if caminho:
        caminho_logo.set(caminho)

# Interface 
janela = tk.Tk()
janela.title("Gerador de QR Code Avançado")
janela.geometry("500x600")

# Entrada de texto
tk.Label(janela, text="Digite o texto ou URL:", font=("Arial", 12)).pack(pady=10)
entrada = tk.Entry(janela, width=50)
entrada.pack(pady=5)

# Botões para escolher cores
cor_qrcode = tk.StringVar()
cor_fundo = tk.StringVar()
tk.Button(janela, text="Escolher cor do QR Code", command=escolher_cor_qr).pack(pady=5)
tk.Button(janela, text="Escolher cor de fundo", command=escolher_cor_bg).pack(pady=5)

# Botão para escolher logo
caminho_logo = tk.StringVar()
tk.Button(janela, text="Adicionar logo (opcional)", command=escolher_logo).pack(pady=5)

# Botão para gerar QR Code
tk.Button(janela, text="Gerar QR Code", command=gerar_qrcode, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10)

# Label para exibir imagem
label_imagem = tk.Label(janela)
label_imagem.pack(pady=20)

janela.mainloop()