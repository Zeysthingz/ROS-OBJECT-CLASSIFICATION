from torchvision import transforms
import torch
from PIL import Image
from vgg import vgg


class Classifier:
    def __init__(self):
        self.device = "cuda"
        self.class_names = ["go", "stop"]
        self.transform = transforms.Compose([transforms.RandomResizedCrop(224), transforms.ToTensor()])
        model = vgg(num_classes=2).to(self.device)
        weight = "/content/gdrive/MyDrive/LeoTask/vgg16/best_model.pth"
        model.load_state_dict(torch.load(weight, map_location=self.device))
        model.eval()
        self.model = model

    def prediction(self, img):
        image = Image.fromarray(img)
        image = self.transform(image)
        image = img.view((1, 3, 224, 224))
        prediction = self.model(image.to(self.device))
        prediction = torch.nn.functional.softmax(prediction)
        prediction = prediction.to("cpu")
        id = torch.max(prediction, dim=1)[1]
        name = self.class_names[int(id)]
        score = float(prediction[0][int(id)])
        return name, score
