import requests


def get_insta_data(username):   
    url = "https://instagram230.p.rapidapi.com/user/details"

    querystring = {"username": username}

    headers = {
        "x-rapidapi-key": "056c5e7c40mshb4b9b0c10ac2bbdp1c5cb0jsn25baa871c836",
        "x-rapidapi-host": "instagram230.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        print("\n=== Profile API Response ===")
        print(data)
        print("=== End of Profile Response ===\n")
        return data
    except Exception as e:
        print(f"Error in get_insta_data: {str(e)}")
        return None


def get_insta_posts(username):
    url = "https://instagram230.p.rapidapi.com/user/posts"

    querystring = {"username": username}

    headers = {
        "x-rapidapi-key": "056c5e7c40mshb4b9b0c10ac2bbdp1c5cb0jsn25baa871c836",
        "x-rapidapi-host": "instagram230.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        print("\n=== Posts API Response ===")
        print(data)
        print("=== End of Posts Response ===\n")
        return data
    except Exception as e:
        print(f"Error in get_insta_posts: {str(e)}")
        return None

