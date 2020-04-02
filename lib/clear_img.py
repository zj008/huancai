import os

base = "./static/img/news"
dirs = os.listdir(base)
for dir in dirs:
    d = os.path.join(base, dir)
    for f in os.listdir(d):
        f_path = os.path.join(d, f)
        os.remove(f_path)