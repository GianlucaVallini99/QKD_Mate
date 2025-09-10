from src.alice_client import alice_client

if __name__ == "__main__":
    client = alice_client()
    resp = client.get("status")
    print("Alice status:", resp)