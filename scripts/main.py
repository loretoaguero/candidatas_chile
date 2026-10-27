def main() -> None:
    from mujeres_en_elecciones.data_loading import load_municipality_data

    datos_2024 = load_municipality_data("voting_by_commune")  # muni["voting"]["2024"]
    print(datos_2024.shape)


if __name__ == "__main__":
    main()
