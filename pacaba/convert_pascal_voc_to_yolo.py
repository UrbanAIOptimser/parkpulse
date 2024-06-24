import shutil
import os
import xml.etree.ElementTree as ET


def convert_annotation(output_file, content, classes):
    in_file = open("datasets/ParkingCarsDataset/Annotations/" + content + ".xml")
    out_file = open(output_file + content + ".txt", "w")
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)

    for obj in root.iter("object"):
        difficult = obj.find("difficult").text
        cls = obj.find("name").text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find("bndbox")
        x_center = float(xmlbox.find("xcenter").text)
        y_center = float(xmlbox.find("ycenter").text)
        width = float(xmlbox.find("width").text)
        height = float(xmlbox.find("height").text)
        # Normalize bounding box coordinates
        x_center_norm = x_center / w
        y_center_norm = y_center / h
        width_norm = width / w
        height_norm = height / h

        yolo8_annotation = (
            x_center_norm,
            y_center_norm,
            width_norm,
            height_norm,
        )  # f"{cls_id} {x_center_norm} {y_center_norm} {width_norm} {height_norm}"

        b = (
            float(xmlbox.find("xcenter").text),
            float(xmlbox.find("ycenter").text),
            float(xmlbox.find("width").text),
            float(xmlbox.find("height").text),
        )
        # bb = convert((w, h), b)
        out_file.write(
            str(cls_id) + " " + " ".join([str(a) for a in yolo8_annotation]) + "\n"
        )


def create_yolo_label(label_dir, contents, classes):
    list_file = open(label_dir + ".txt", "w")

    for content in contents:
        list_file.write(content + "\n")
        convert_annotation(label_dir, content, classes)
    list_file.close()


def move_image_yolo(contents, source_img_dir_path, dest_img_dir):
    for content in contents:
        image_path = os.path.join(source_img_dir_path, f"{content}.jpg")

        if os.path.exists(image_path):
            destination_image_path = os.path.join(dest_img_dir, f"{content}.jpg")

            shutil.copy(image_path, destination_image_path)
            print(f"Copy {content}.jpg to {dest_img_dir}")
        else:
            print(f"Image {content}.jpg not found in {image_path}")


def get_contents(img_dir_path, dir_):
    with open(img_dir_path + f"Main/{dir_}.txt", "r") as f:
        contents = f.read().splitlines()
    return contents


if __name__ == "__main__":
    classes = ["vehicle"]
    prep_dir = ["train", "test", "trainval", "val"]
    img_dir_path = "datasets/ParkingCarsDataset/ImageSets/"
    yolo_dir_path = "datasets/ParkingCarsDataset/yolo/"
    source_img_dir_path = "datasets/ParkingCarsDataset/Images_Masked1/"

    for dir_ in prep_dir:
        img_dir = yolo_dir_path + f"{dir_}/images/"
        label_dir = yolo_dir_path + f"{dir_}/labels/"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)

        contents = get_contents(img_dir_path, dir_)
        create_yolo_label(label_dir, contents, classes)
        move_image_yolo(contents, source_img_dir_path, img_dir)
