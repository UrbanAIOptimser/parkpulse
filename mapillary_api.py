import requests
import os
import time

client_id = "7434019660018583"
access_token = "MLY|7434019660018583|443320a03353a936b04148c98e858b3a"
bbox = [2.0, 41.3, 2.3, 41.5]
object_value = "information--parking--g*"  # Wildcard search
limit = 5
total_limit = 10
current_count = 0

# Directory where images will be saved
directory = "mapillary_folder"
os.makedirs(directory, exist_ok=True)

map_feature_url = "https://graph.mapillary.com/map_features"
page = 0
more_features = True

while current_count < total_limit and more_features:
    params = {
        "access_token": access_token,
        "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "object_values": object_value,
        "fields": "id,images",
        "limit": limit,
        "page": page,
    }

    try:
        map_feature_response = requests.get(map_feature_url, params=params, timeout=10)
        map_feature_response.raise_for_status()
        map_features = map_feature_response.json()["data"]
        print(f"Fetched {len(map_features)} map features on page {page}")

        if not map_features:
            print("No more map features found, stopping")
            more_features = False
        else:
            for feature in map_features:
                images = feature["images"]["data"]  # Extract the list of image dictionaries
                for image_info in images:
                    image_id = image_info["id"]  # Extract the ID from each dictionary
                    print(f"Image ID: {image_id}")
                    image_url = f"https://graph.mapillary.com/{image_id}"
                    print(f"Fetching image URL: {image_url}")

                    image_response = requests.get(image_url, params={
                        "access_token": access_token,
                        "fields": "id,thumb_1024_url"
                    }, timeout=10)
                    image_response.raise_for_status()
                    image_data = image_response.json()
                    thumbnail_url = image_data["thumb_1024_url"]
                    print(f"Found thumbnail URL for image {image_id}")

                    # Download the image
                    image_content_response = requests.get(thumbnail_url, timeout=10)
                    image_content_response.raise_for_status()
                    image_path = os.path.join(directory, f"parking_{image_id}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(image_content_response.content)
                    current_count += 1
                    print(f"Downloaded {image_path}")

                    if current_count >= total_limit:
                        print("Total limit reached, stopping further downloads")
                        more_features = False
                        break

            page += 1
            time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching map features: {e}")
        more_features = False
        break
