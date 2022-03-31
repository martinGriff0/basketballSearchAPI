import os
from fastapi import FastAPI
from sqlalchemy.sql.expression import and_
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import random
# from components.Search import CustomSearch, GetPlayerPage, RandomSearch
# from components.Models import Item
# from db.basketball_stats import engine
from sqlalchemy import create_engine
from pydantic import BaseModel


app = FastAPI()

engine = create_engine("mysql+pymysql://admin:SageJutsu69@basketball-search.cq86yhnzjvtt.us-east-1.rds.amazonaws.com/sys", echo=True, future=True)

class intSubItem(BaseModel):
    string: str
    value: str
    operator: str
    id: str

class subItem(BaseModel):
    string: str
    value: str

class Item(BaseModel):
    Name: subItem
    POS: subItem
    TM: subItem
    LowerYear: intSubItem
    UpperYear: intSubItem
    AGE: intSubItem
    AST: intSubItem
    RB: intSubItem
    STL: intSubItem
    BLK: intSubItem
    PTS: intSubItem


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000/",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# engine = create_engine("mysql+pymysql://root:ilikemen69@127.0.0.1/Basketball", echo=True, future=True)

@app.get("/")
async def root():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT Year FROM per_game_seasons ORDER BY Year DESC"))
        response = result.all()
        return response
    except Exception as ex:
        return ex

@app.post("/")
async def ccustom_search(item: Item):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(CustomSearch(item)))
        response = result.all()
        return response
    except:
        return "Error", "There was an Error"

    
@app.post("/RandomSearch")
async def random_search(count: int):
    try:
        response = RandomSearch(count)
        return response
    except:
        return "Error", "There was an Error, please try again"

@app.get("/Player")
async def get_player_page(playerName: str):
    try:
        response = GetPlayerPage(playerName)
        return response
    except:
        return "There was an Error"

@app.post("/RandomSearch/Quiz")
async def quiz_question():
    try:
        randomSearch = RandomSearch(6)
        print("Method finished")
        nameArray = []
        for season in randomSearch[0]:
            if "*" in season[2]:
                name = season[2].replace("*", "")
                if name not in nameArray:
                    nameArray.append(name)
            else:
                if season[2] not in nameArray:
                    nameArray.append(season[2])
        amount = len(randomSearch[0]), len(nameArray)
        hint = randomSearch[0][0][1], randomSearch[0][0][5], randomSearch[0][0][3]
        return randomSearch[1], nameArray, amount, hint
    except:
        return "Error", "There was an Error, please try again"

@app.get("/Leaderboard/Top")
async def current_leader():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT leaderboardId AS id, Name, Score FROM leaderboard ORDER BY Score DESC"))
        response = result.all()
        return response
    except:
        return "Error", "There was an Error, please try again"

@app.post("/Leaderboard/Add")
async def add_score(name: str, score: int):
    try:
        with engine.connect() as conn:
            finalName = name.strip()
            conn.execute(text('INSERT INTO leaderboard (Name, Score) VALUES ("{0}", {1})'.format(finalName, score)))
            conn.commit()
        return "Success"
    except:
        return "Error", "There was an Error, please try again"

def GetValue(category: str):
    if category == "PTS":
        return random.randrange(5, 39), ">"
        # return round((random.random() * 35) + 5, 1)
    elif category == "AGE":
        return random.randrange(20, 36), random.choice(Operators)
    elif category == "AST" or category == "RB":
        return random.randrange(3, 18), ">"
        # return round((random.random() * 15) + 3, 1)
    elif category == "BLK" or category == "STL":
        return random.randrange(1, 5), ">"
        # return round((random.random() * 5) + .5, 1)
    elif category == "TOV":
        return random.randrange(1, 5), "<"
    elif category == "Year":
        return random.randrange(1959, 2020), random.choice(Operators)


def CustomSearch(item: Item):
    searchString = "select * from per_game_seasons where "
    count = 0
    for ite in item:
        if ite[1].value and ite[1].value.strip():
            if count > 0:
                searchString = searchString + " AND "
            if ite[1].string in IntSubItems:
                searchString = searchString + ite[1].string + " " + ite[1].operator + " " + ite[1].value
            else:
                searchString = searchString + ite[1].string + " like '%" + ite[1].value + "%'"
            count = count + 1
    return searchString + " ORDER BY Year Desc"

def RandomSearch(num: int):
    tIntsubItems = list(IntSubItems)
    tIntsubItems.remove("Year")
    count = num + 1
    searchString = "select * from per_game_seasons where "
    times = 0
    operator = ">"
    with engine.connect() as conn:
        while count > num or count == 0 :
            if count == 0 or times >= len(IntSubItems):
                searchString = "select * from per_game_seasons where "
                tIntsubItems = list(IntSubItems)
                tIntsubItems.remove("Year")
                times = 0
            intSubItem = random.choice(tIntsubItems)
            tIntsubItems.remove(intSubItem)
            value, operator = GetValue(intSubItem)
            # operator = random.choice(Operators)


            if times == 0:
                searchString = searchString + intSubItem + " " + operator + " " + str(value)
            else:
                searchString = searchString + " AND " + intSubItem + " " + operator + " " + str(value)
            result = conn.execute(text(searchString))
            response = result.all()
            count = len(response)
            times = times + 1

        print("querying complete")
        finalSearchString = searchString.removeprefix("select * from per_game_seasons where ")
        return response, finalSearchString

    
def GetPlayerPage(playerName: str):
    with engine.connect() as conn:
        result = conn.execute(text('select * from per_game_seasons where name = "{0}" ORDER By Year'.format(playerName)))
        seasonStats = result.all()
        positions = []
        teams = []
    for season in seasonStats:
        if (season[3] not in positions):
            if '-' in season[3]:
                twoPos = season[3].split('-')
                for pos in twoPos:
                    positions.append(pos)
            else:
                positions.append(season[3])
            positions = list(dict.fromkeys(positions))
        if (season[5] not in teams):
            if season[5] != "TOT":
                teams.append(season[5])
    bestSeasons = GetMaxSeasons(seasonStats)
    return seasonStats, teams, positions, bestSeasons



IntSubItems = [ "Year", "AST", "PTS", "RB", "STL", "BLK", "AGE", "TOV" ]
# IntSubItems = [ "Year", "AST", "PTS", "RB", "STL", "BLK", "AGE", "TOV", "FG", "FGA", "FGPer", "3P", "3PA", "3PPer" ]

Operators = [">", "<"]

def GetMaxSeasons(seasonStats: list):
    maxPTS = [0, 0]
    maxAST = [0, 0]
    maxRB = [0, 0]
    maxSTL = [0, 0]
    maxBLK = [0,0]
    for season in seasonStats:
        if (season[27] > maxPTS[0]):
            maxPTS = season[27], season[1], "Points"
        if (season[22] > maxAST[0]):
            maxAST = season[22], season[1], "Assists"
        if (season[21] > maxRB[0]):
            maxRB = season[21], season[1], "Rebounds"
        if (season[23]):
            if (season[23] > maxSTL[0]):
                maxSTL = season[23], season[1], "Steals"
            if (season[24] > maxBLK[0]):
                maxBLK = season[24], season[1], "Blocks"
    return maxPTS, maxAST, maxRB, maxSTL, maxBLK
