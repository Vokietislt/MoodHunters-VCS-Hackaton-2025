from dbfunctions import EmotionLogDB  

db = EmotionLogDB()
db.read_logs()
db.close()