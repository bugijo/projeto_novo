import pyautogui
import time

print("Posicione o mouse na área desejada na tela...")
time.sleep(5)  # Espera 5 segundos para que você possa mover o mouse
x, y = pyautogui.position()  # Captura as coordenadas atuais do mouse
print(f"As coordenadas do mouse são: X={x}, Y={y}")
