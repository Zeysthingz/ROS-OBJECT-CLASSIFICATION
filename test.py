from dataset_loader import CustomImageDataset
from torch.utils.data import DataLoader
from vgg import vgg
from torchvision import transforms
import torch

"""
with torch.no_grad():
    # predict class
    output = torch.squeeze(model(img.to(device))).cpu()
    predict = torch.softmax(output, dim=0)
    predict_cla = torch.argmax(predict).numpy()
"""


def main():
    device = "cuda"

    data_transform = transforms.Compose([transforms.RandomResizedCrop(224)])
    test_data = CustomImageDataset("/content/gdrive/MyDrive/my_dataset/test", transform=data_transform)
    test_loader = DataLoader(dataset=test_data, batch_size=1)
    model = vgg(model_name="vgg16", num_classes=test_data.num_class, init_weights=True).to(device)
    model_weight_path = "/content/gdrive/MyDrive/LeoTask/vgg16/best_model.pth"
    model.load_state_dict(torch.load(model_weight_path, map_location=device))

    model.eval()

    total_num = len(test_loader.dataset)
    sum_num = torch.zeros(1).to(device)

    tpositive = 0
    tnegative = 0
    fpositive = 0
    fnegative = 0

    for images, labels in test_loader:
        pred = model(images.to(device))
        pred = torch.max(pred, dim=1)[1]
        pred = pred.to("cpu")
        if (pred == 0 and labels == 0):
            tpositive += 1
        elif (pred == 1 and labels == 1):
            tnegative += 1
        elif (pred == 0 and labels == 1):
            fpositive += 1
        elif (pred == 1 and labels == 0):
            fnegative += 1

    precision = tpositive / (tpositive + fpositive)
    recall = tpositive / (tpositive + fnegative)
    f1_score = 2 * ((precision * recall) / (precision + recall))
    test_acc = (tpositive + tnegative) / total_num
    print("Precision {}".format(precision))
    print("Recall {}".format(recall))
    print("f1_score {}".format(f1_score))
    print("test_acc {}".format(test_acc))


if __name__ == "__main__":
    main()
