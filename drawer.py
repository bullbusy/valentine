from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# from PIL import ImageColor
# from duotone import Duotone
import time


# получает адресс шаблона, имена отправителя и получателя
# возвращает адресс готовой валентинки
def draw(imagine, from_name, to_name):
    img = Image.open(imagine)
    print("image is loaded")
    font = None

    # Підключення шрифту.
    try:
        font = ImageFont.truetype("SFProDisplayBlack.ttf", 48)
        print("Font loading successful.")
    except:
        print("Font loading failed.")
        return

    # Фарбування зображення "дуотон".
    '''
    start = time.time()

    # Світлий та темний колір для ефекту дуотону.
    light_values = ImageColor.getrgb('#FC1972')
    dark_values = ImageColor.getrgb('#420642')

    try:
        duotone_coloring = Duotone.process(img, light_values, dark_values, 0.5)
        print("Duotoning process successful.")
    except:
        print("Duotoning process failed.")
    
    end = time.time()
    print(end - start)
    
    # Переприсвоєння об'єкту
    img = duotone_coloring
    '''

    draw = ImageDraw.Draw(img)

    # Створення надпису від кого валентинка.
    draw.text((48, 495), ("від " + from_name), (255, 255, 255), font=font)
    # Створення надпису для кого валентинка.
    draw.text((48, 555), ("для " + to_name), (255, 255, 255), font=font)
    img.save("sample_out.jpg")
    return 'sample_out.jpg'
    # return imagine


if __name__ == "__main__":
    draw("sample.jpg", "@bullbusy", "@bl_B_A_H")
