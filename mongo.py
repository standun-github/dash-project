"""Testing out database connection"""

import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://test:uToLGHDvKG87XsPC@cluster0.yejqf4u.mongodb.net/?retryWrites=true&w=majority")
db = client["mydb"]

if __name__ == "__main__":

    post = {"_id": 1, "num_rows": 2, "num_cols": 2}
    db["newCollection"].delete_one(post)
    post = {"_id": 1, "payoff": "[{'0': '2,1', '1': '0,0'},{'0': '0,0', '1': '1,2'}]"}
    db["elements"].delete_one(post)

    input_data = [{'0': '2,1', '1': '0,0', '2': '0,0'}, {'0': '0,0', '1': '1,2', '2': '1,2'}]
    # get last element ID
    table_id = db["newCollection"].count_documents({})
    print(table_id)
    num_rows = 2

    count = 0
    for i in range(num_rows):
        for val in input_data[i].values():
            count += 1
            print(val)
            post = {"_id": count, "foreign_id": table_id, "payoff": val}
            db["elements"].insert_one(post)

    post = {"_id": 1, "num_rows": 2, "num_cols": 3}
    db["newCollection"].insert_one(post)

    # get last id
    table_id = db["newCollection"].count_documents({})
    print("count docs:", table_id)

    # get details of last element by id
    num_rows = 0
    num_cols = 0
    results = db["newCollection"].find({"_id": table_id})
    for x in results:
        num_rows = x["num_rows"]
        num_cols = x["num_cols"]

    print(num_rows)
    print(num_cols)

    data_list = []
    results = db["elements"].find({"foreign_id": 0})

    count = 0
    new_dict = {}
    for x in results:
        new_dict[count] = x["payoff"]
        count += 1
        if (count % num_cols == 0):
            data_list.append(new_dict)
            new_dict = {}

    print(data_list)

    examples = [{"name": "Battle of the sexes", "id": 1},
                {"name": "Prisoner\'s dilemma", "id": 2},
                {"name": "Rock, paper, scissors", "id": 3},
                {"name": "Matching pennies", "id": 4},
                {"name": "Stag hunt", "id": 5},
                {"name": "Recently saved game..", "id": 6}]

    print("Stag hunt" in e["name"] for e in examples)
