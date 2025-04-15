import pygame
from transformers import BlenderbotForConditionalGeneration, BlenderbotTokenizer

# 🔹 Инициализация pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("AI Ассистент")

# 🔹 Загрузка изображений
neutral_face = pygame.image.load("neutral.png")
talking_face = pygame.image.load("talking.png")
current_face = neutral_face

# 🔹 Настройка модели BlenderBot (ИИ-диалоги)
model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-400M-distill")
tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-400M-distill")

def ai_talk(text):
    inputs = tokenizer([text], return_tensors="pt")
    reply_ids = model.generate(**inputs)
    return tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]

def animate_ai(text):
    global current_face
    current_face = talking_face
    response = ai_talk(text)
  #  speak(response)
    current_face = neutral_face

running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(current_face, (100, 100))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()