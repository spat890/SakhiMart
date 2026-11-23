"""Member 3: Basic OpenCV image quality checks (not an AI classifier)."""
import argparse
from pathlib import Path
import cv2

def inspect_image(path):
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Could not open image: {path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    issues = []
    if blur_score < 80:
        issues.append("Image may be blurry; retake with steady hands.")
    if brightness < 55:
        issues.append("Image may be too dark; use better lighting.")
    elif brightness > 210:
        issues.append("Image may be overexposed; reduce direct light.")
    return {
        "width": int(image.shape[1]), "height": int(image.shape[0]),
        "blur_score": round(blur_score, 2),
        "brightness": round(brightness, 2),
        "status": "NEEDS IMPROVEMENT" if issues else "ACCEPTABLE",
        "suggestions": issues or ["Image passed the basic blur and brightness checks."]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to a product image")
    args = parser.parse_args()
    try:
        result = inspect_image(Path(args.image))
        for key, value in result.items():
            print(f"{key}: {value}")
    except (ValueError, cv2.error) as error:
        print("ERROR:", error)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
