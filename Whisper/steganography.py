import os
from stegano import lsb


""" გადავწყვიტე ყველა შვილობილ კლასს თავისი ფუნქციონალი მივანიჭო, ყველა ეს კლასი სთავესც იღებს class Steganography-ის გან
     ,შემგდომ მოდის   TextSteganography, რომელშიც უშუალოდ ტექსტის ფოტოში ჩამალვის ფუნქციონალი აკისრია და ასე გაგრზელდება 
     იქამდე სანამ პუ არ დააკმყოფილებს ყველაც საჭირო მოთხოვნასა და ფუნქციონალს, ეს არის ოოპში სწორი მიდგომა,რიტიც კოდიბ ხდება
      უფრო მარტივად აღსაქმელი და წაკითხვადი.  
"""

class Steganography:
    def __init__(self):
        pass

    def Check_Content(self):
        pass


class TextSteganography(Steganography):
    def __init__(self):
        self.img_path = ''
        self.secret_message = ''
        self.output_img = ''

    def Cheak_Content(self,img_path):

        """ეს არის მეთოდი რომერლიც იღებს არგუმენტად ფოტოს და ამოწმებს შეიცავს თუ არა კონტენტს
           თუმცა ხდება კონტენტის ამორება, რამაც შეიზლება საფრტხე შეუქმნას უსაფრტხოებას, რადგან არის ალბატობა
           რომ კომტენტმა გაჯონოს. ამ საშისროების პრევენციის მიზნით კონტენტი არსად ინახება და არ იბეჭდება.
           ერთადერთი იგი ინახება მხოლოდ სტრიქონსიო, რომლის სიგრზეც მოწმდება და დგინდება შეიცავს თუ არა იგი კონტენტს.ძ
        """
        self.img_path = img_path
        try:
            if not os.path.exists(self.img_path):
                return f"Error: Image file not found: {self.img_path}"
            hide_content = lsb.reveal(self.img_path)
            check_size = lambda hide_content : hide_content and len(hide_content) > 0
            return check_size(hide_content)
        except Exception as e:
              return f"error {str(e)} "

    def set_parameters(self,img_path,secret_message,output_img):
        self.img_path = img_path
        self.secret_message = secret_message
        self.output_img = output_img
        return "Done"


    def encode_info(self, img_path: str, secret_message: str, output_img: str) -> str:
        """
        დაშიფრის მეთოდი, იღებს სამ პარამეტრს,დასამალ შეტყობინებას, შემავალ და გამომავალ ფოტოს.
        """
        parameters = self.set_parameters(img_path,secret_message,output_img)
        print( parameters )
        try:
            if not os.path.exists(self.img_path):# მოწმდება ფაილის არსებობა
                return f"Error: Image file not found: {self.img_path}"
            secret_image = lsb.hide(self.img_path, self.secret_message)#მალავს მესიჯს ფოტოში
            secret_image.save(self.output_img)#ინახასვს დამალიულ ფაილს
            return f"Message successfully hidden in: {self.output_img}"
        except Exception as e:
            return f"Encoding error: {e}"

    def decode_info(self, img_path: str) -> str:
        """
        ერთპარამეტრიანი მეტოდი, რომელის პასუხისმგერბელია დეკოდზე
        """
        self.img_path = img_path
        try:
            if not os.path.exists(self.img_path):
                return f"Error: Image file not found: {self.img_path}"
            return lsb.reveal(self.img_path) or "No hidden message found."
        except Exception as e:
            return f"Decoding error: {e}"

    # def convert_to_Png(self, img_path: str) -> str:
    #     try:
    #         img = Image.open(img_path)
    #         new_path = os.path.splitext(img_path)[0] + ".png"
    #         img.save(new_path, "PNG")
    #         return new_path
    #     except Exception as e:
    #         return f"Conversion error: {e}"

    def read_from_file(self, file_name: str) -> str:
        """
        Read text content from a file.
        """
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "File not found."



