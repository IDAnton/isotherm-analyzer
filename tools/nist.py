import numpy as np
import pandas as pd


class Reader:
    def __init__(self):
        pass

    def clean_txt(self, file_path):
        data = pd.read_csv(file_path)

        pressures = data.iloc[:,1].to_numpy()
        adsorption = data.iloc[:,3].to_numpy()
        print(adsorption)


if __name__ == "__main__":
    r = Reader()
    r.clean_txt("DUT-49.txt")
