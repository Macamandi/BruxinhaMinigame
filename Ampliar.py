# Nome do arquivo: Ampliar.py
import serial
import pygame
from serial.tools import list_ports

# --- PALETAS DE CORES PRÉ-DEFINIDAS ---
PALETTES = {
    "1: OLED (Amarelo e Azul)": { "top": (255, 255, 0), "main": (60, 180, 255), "bg": (10, 10, 20) },
    "2: Âmbar (Estilo Osborne)": { "top": (255, 255, 255), "main": (223, 113, 38), "bg": (32, 35, 13) },
    "3: Verde Fósforo (Retrô)": { "top": (187, 214, 195), "main": (50, 255, 50), "bg": (10, 20, 10) },
    "4: Invertido (Padrão)": { "top": (0, 0, 0), "main": (0, 0, 0), "bg": (255, 255, 255) },
	"5: Preto & Branco (Simplicidade)": { "top": (255, 255, 255), "main": (255, 255, 255), "bg": (0, 0, 0) },
	"6: Alexandre (Lá ele)": { "top": (95, 205, 228), "main": (215, 123, 186), "bg": (172, 50, 50) }
}


# --- FUNÇÃO PARA SELEÇÃO DE PORTA ---
def select_port():
    print("Procurando portas seriais disponíveis...")
    ports = list_ports.comports()
    if not ports:
        print("ERRO: Nenhuma porta serial foi encontrada.")
        return None
    print("Portas encontradas:")
    for i, port in enumerate(ports):
        print(f"  {i + 1}: {port.device} - {port.description}")
    while True:
        try:
            choice = int(input("\nDigite o número da porta onde o Arduino está conectado: "))
            if 1 <= choice <= len(ports):
                return ports[choice - 1].device
            else:
                print("Número inválido.")
        except (ValueError, KeyboardInterrupt):
            print("\nSeleção inválida ou cancelada.")
            return None

# --- FUNÇÃO PARA SELEÇÃO DE PALETA ---
def select_palette():
    print("\nSelecione uma paleta de cores:")
    palette_keys = list(PALETTES.keys())
    for key in palette_keys:
        print(f"  {key}")
    
    while True:
        try:
            choice = int(input("\nDigite o número da paleta desejada: "))
            if 1 <= choice <= len(palette_keys):
                return PALETTES[palette_keys[choice - 1]]
            else:
                print("Número inválido.")
        except (ValueError, KeyboardInterrupt):
            print("\nSeleção inválida ou cancelada.")
            return None


# --- CONFIGURAÇÕES ---
BAUD_RATE = 500000 # Velocidade de transmissão serial
GAME_WIDTH, GAME_HEIGHT = 128, 64
SCALE_FACTOR = 10

# --- INICIALIZAÇÃO ---
arduino_port = select_port()
if not arduino_port:
    exit()

selected_palette = select_palette()
if not selected_palette:
    exit()

TOP_COLOR = selected_palette["top"]
MAIN_COLOR = selected_palette["main"]
BACKGROUND_COLOR = selected_palette["bg"]


print(f"\nTentando conectar à porta {arduino_port}...")
try:
    arduino = serial.Serial(arduino_port, BAUD_RATE, timeout=2)
    print("Conectado com sucesso! Iniciando monitor...")
    print("Pressione ESC para sair.")
except serial.SerialException as e:
    print(f"ERRO: Não foi possível conectar: {e}")
    input("Pressione Enter para sair.")
    exit()

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Espelho do Jogo em Arduino")

running = True

# --- LOOP PRINCIPAL ---
while running:
    # Captura de eventos (teclado, mouse, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                arduino.write(b'U')
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                arduino.write(b'D')
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                arduino.write(b'L')
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                arduino.write(b'R')

    # Leitura e renderização do display
    try:
        arduino.read_until(b'S')
        frame_buffer = arduino.read(GAME_WIDTH * GAME_HEIGHT // 8)

        if len(frame_buffer) == 1024:
            screen.fill(BACKGROUND_COLOR)
            
            for i, byte in enumerate(frame_buffer):
                x = i % GAME_WIDTH
                page = i // GAME_WIDTH
                
                for bit_index in range(8):
                    if (byte & (1 << bit_index)):
                        y = (page * 8) + bit_index
                        pixel_color = TOP_COLOR if y < 16 else MAIN_COLOR
                        pygame.draw.rect(screen, pixel_color, 
                                         (x * SCALE_FACTOR, y * SCALE_FACTOR, 
                                          SCALE_FACTOR, SCALE_FACTOR))
            
            pygame.display.flip()

    except serial.SerialException as e:
        print(f"\nERRO: Conexão com o Arduino perdida: {e}")
        running = False
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        running = False

# --- FINALIZAÇÃO ---
print("\nFechando conexão e saindo.")
arduino.close()
pygame.quit()
