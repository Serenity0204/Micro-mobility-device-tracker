import face_recognition
from django.core.files.storage import default_storage


def recognize_faces_util(owner_image_path, test_path):
    # Load and encode owner's face
    owner_image = face_recognition.load_image_file(owner_image_path)
    owner_encoding = face_recognition.face_encodings(owner_image)[0]

    # Load and encode test image
    test_image = face_recognition.load_image_file(default_storage.path(test_path))
    test_locations = face_recognition.face_locations(test_image)
    test_encodings = face_recognition.face_encodings(test_image, test_locations)

    # Compare faces
    results = []
    for encoding in test_encodings:
        match = face_recognition.compare_faces([owner_encoding], encoding, tolerance=0.45)
        results.append("Owner Detected ✅" if match[0] else "Unknown ❌")
    return results