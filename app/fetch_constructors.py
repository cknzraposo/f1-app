from f1_constructors import fetch_all_constructors, save_constructors

if __name__ == "__main__":
    data = fetch_all_constructors()
    save_constructors(data)
