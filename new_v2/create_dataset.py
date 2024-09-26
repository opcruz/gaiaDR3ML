import os

import pandas as pd

stars_files = [
    ("./normalized/SY.csv", 0),
    ("./normalized/PN.csv", 1),
    ("./normalized/Be.csv", 2),
    ("./normalized/CV.csv", 3),
    ("./normalized/Mira.csv", 4),
    ("./normalized/Ae.csv", 5),
    ("./normalized/YSO.csv", 6),
    ("./normalized/WR.csv", 7),
    ("./normalized/pAGB.csv", 8),
    ("./normalized/TT.csv", 9)
]

limit = 1000
result = []
for file in stars_files:
    df1 = pd.read_csv(file[0], header=None)
    size = min(len(df1), limit)
    df1 = df1.sample(size, random_state=10)
    df1 = df1.assign(id=file[1])
    result.append(df1)

df_result = pd.concat(result)

out_dir = './datasets'
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
fullname = os.path.join(out_dir, "unbalanced_1000.csv")
df_result.to_csv(fullname, header=False, index=False)
