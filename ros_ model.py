from torchvision import transforms
import torch
from PIL import Image
from vgg import vgg

class Classifier:
    def __init__(self,device):
        self.device = device
        self.class_names = ["go","stop"]
        self.transform = transforms.Compose([transforms.RandomResizedCrop(224),transforms.ToTensor()])

        model = vgg(num_classes=2).to(device)
        weight = "/content/gdrive/MyDrive/LeoTask/vgg16/best_model.pth"
        model.load_state_dict(torch.load(weight, map_location=device))
        model.eval()
        self.model = model
    def prediction(self,img):
        image = Image.fromarray(img)
        image = self.transform(img)
        image= img.view((1,3,224,224))
        prediction = self.model(img.to(self.device))
        prediction = torch.nn.functional.softmax(pred)
        prediction = prediction.to("cpu")
        id = torch.max(prediction, dim=1)[1]
        name = self.class_names[int(id)]
        score = prediction[0][int(id)]
        return name,float(score)