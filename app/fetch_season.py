from f1_results import fetch_season_results, save_results

if __name__ == "__main__":
    for year in range(1984, 2025):  # adjust end year
        data = fetch_season_results(year)
        save_results(year, data)
