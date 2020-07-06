from pymongo import MongoClient
import requests
from io import BytesIO
import gridfs

def getConnection(host):
    dbName1 = 'mongodbproject'
    dbName2 = 'amazonImages'
    client = MongoClient(host)
    dbP = client[dbName1]
    dbI = client[dbName2]
    amazon_img = dbP['amazon_phone_dataset']
    imageCol = dbI['Images']

    return dbP, dbI, amazon_img, imageCol


def getData(pCol):
    q = [
        {
            '$match': {'Product_img': {'$exists': True}}
        },
        {
            '$project': {'_id': 1, 'Product_img': 1}
        }
    ]

    result = list(pCol.aggregate(q))
    return result

def insertData(db,iCol,data):
    fs = gridfs.GridFS(db)
    imageList = []
    i = 0
    for record in data:
        try:
            print("image # : {} | fetching image: {}".format(i, record['Product_img']))
            r = requests.get(record['Product_img'])
            img = fs.put(BytesIO(r.content))
            # pilImage = Image.open(BytesIO(r.content))
            # w, h = pilImage.size
            # new_w = w // 4
            # new_h = h // 4
            # im = pilImage.resize((new_w, new_h))
            # im = np.asarray(im)
            # im = im.tostring()
            # im = fs.put(im, encoding='utf-8')
            curr = {'_id':record['_id'], 'imgSrc': img}
            imageList.append(curr)
            iCol.insert_one(curr)
            # time.sleep(0.1)
            i = i+1
            # if i==5:
            #     break
        except Exception as e:
            print("error due to {}".format(e))
    # iCol.insert_many(imageList)
    # iCol.insert_one()

def inImage(host):
    dbP, dbI, pCol, iCol = getConnection(host)
    result = getData(pCol)
    insertData(dbI, iCol, result)

if __name__ == '__main__':
    inImage('mongodb+srv://muriel82:Muriel824@cluster0-kxon7.mongodb.net/test?retryWrites=true&w=majority')