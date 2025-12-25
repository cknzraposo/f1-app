from f1_drivers import fetch_all_drivers, save_drivers

if __name__ == "__main__":
    data = fetch_all_drivers()
    save_drivers(data)
