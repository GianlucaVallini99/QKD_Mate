from src.bob_client import bob_client

if __name__ == "__main__":
    client = bob_client()
    resp = client.get("status")
    print("Bob status:", resp)
