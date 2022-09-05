import json
import pymongo

# Database connection
client = pymongo.MongoClient(
    "mongodb+srv://test:uToLGHDvKG87XsPC@cluster0.yejqf4u.mongodb.net/?retryWrites=true&w=majority")
db = client["mydb"]


class Table():
    def __init__(self, create_new=True, name="", row_size=2, col_size=2, data=[]):
        self.row_size = row_size
        self.col_size = col_size

        if not name:
            self.columns = [{"name": str(col), "id": str(col)} for col in range(self.col_size)]
            if create_new:
                d = []
                for row in range(0, self.row_size):
                    row_data = {}
                    for col in range(0, self.col_size):
                        row_data[str(col)] = ""
                    d.append(row_data)
                self.data = d
            else:
                self.data = data
        else:
            f = open('sample_games.json')
            examples = json.load(f)

            for ex in examples['sample_games']:
                # print(ex["name"])
                if name == ex["name"]:
                    # print(name, ex["data"], ex["columns"])
                    self.data = ex["data"]
                    self.columns = ex["columns"]
                    self.row_size = len(self.data)
                    self.col_size = len(self.data[0])
                    self.name = ex["name"]

    def get_data(self):
        return self.data

    def get_columns(self):
        return self.columns

    def get_col_size(self):
        return self.col_size

    def get_row_size(self):
        return self.row_size

    def retrieve_data(self):
        table_id = db["newCollection"].count_documents({})
        results = db["newCollection"].find({"table_id": table_id})
        for x in results:
            self.row_size = x["num_rows"]
            self.col_size = x["num_cols"]

        self.data = []
        count = 0
        new_dict = {}
        results = db["elements"].find({"table_id": table_id})
        for x in results:
            new_dict[str(count)] = x["payoff"]
            count += 1
            if count % self.col_size == 0:
                self.data.append(new_dict)
                count = 0
                new_dict = {}

        self.columns = [{"name": str(col), "id": str(col)} for col in range(self.col_size)]

        print("data_list: ", self.data)
        print("col_list: ", self.columns)

        return self.data, self.columns

    def add_records(self):
        table_id = db["newCollection"].count_documents({}) + 1
        post = {"table_id": table_id, "num_rows": self.row_size, "num_cols": self.col_size}
        db["newCollection"].insert_one(post)
        count = 0
        for i in range(self.row_size):
            for val in self.data[i].values():
                count += 1
                print(val)
                post = {"element_id": count, "table_id": table_id, "payoff": val}
                db["elements"].insert_one(post)


if __name__ == "__main__":
    t = Table(col_size=2, row_size=2)
    print(t.get_data())
    print(t.get_columns())
    t2 = Table(name="Stag hunt")
    print(t2.get_data())
    print(t2.get_columns())
    t3 = Table()
    t3.retrieve_data()
    print(t3.get_data())
    print(t3.get_columns())
    t4 = Table(col_size=2, row_size=2, data=[{'0': '1,1', '1': '2,2'}, {'0': '3,3', '1': '4,4'}])
    t4.add_records()


