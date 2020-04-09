import os

os.mkdir("..static")

os.mkdir("..static/img")

av = "..static/img/avatar"
news = "..static/img/news"
team = "..static/img/team"

os.mkdir(av)
os.mkdir(news)
os.mkdir(team)

for i in range(97, 97+26):
    f = chr(i)
    d = os.path.join(news, f)
    os.mkdir(d)

