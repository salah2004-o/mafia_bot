import os
from typing import Optional

BASE_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(BASE_DIR, "images")

LOCAL_IMAGE_MAP = {
    "godfather_img": os.path.join(IMAGES_DIR, "العراب.jpg"),
    "hitman_img": os.path.join(IMAGES_DIR, "القاتل.jpg"),
    "doctor_img": os.path.join(IMAGES_DIR, "الطبيب.jpg"),
    "detective_img": os.path.join(IMAGES_DIR, "محقق.jpg"),
    "citizen_img": os.path.join(IMAGES_DIR, "مواطن.jpg"),
    "jester_img": os.path.join(IMAGES_DIR, "جوكر.jpg"),
    "bodyguard_img": os.path.join(IMAGES_DIR, "الحارس.jpg"),
    "security_guard_img": os.path.join(IMAGES_DIR, "الحارس.jpg"),
}


def get_image_source(image_key: str) -> Optional[str]:
    path = LOCAL_IMAGE_MAP.get(image_key)
    if path and os.path.isfile(path):
        return path
    return None
