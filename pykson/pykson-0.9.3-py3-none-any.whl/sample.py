from pykson import JsonObject, Pykson, IntegerField, StringField, ObjectListField, ListField, DateField, DateTimeField, TimestampSecondsField, ObjectField, JsonField
import pykson

#
# class Score(JsonObject):
#     score = IntegerField()
#     course = StringField()
#
#     def __str__(self):
#         return str(self.course) + ": " + str(self.score)
#
#
# class Student(JsonObject):
#
#     first_name = StringField(serialized_name="fn")
#     last_name = StringField()
#     age = IntegerField()
#     birth = DateField(serialized_name='b')
#     birth_time = TimestampSecondsField(serialized_name='bt')
#     # scores = ListField(int)
#     # scores = ObjectListField(Score)
#     score = Score()
#
#     def __str__(self):
#         return "first name:" + str(self.first_name) + ", last name: " + str(self.last_name) + ", birth: " + str(self.birth_time) + ", age: " + str(self.age) + ", score: " + str(self.score)
#
#
# # print(JsonObject.get_fields(Student))
#
#
# # json_text = '{"fn":"ali", "last_name":"soltani", "age": 25, "scores": [ 20, 19]}'
# # json_text = '{"fn":"ali", "last_name":"soltani", "b":"2015-10-21", "bt": 1553717064, "age": 25, "scores": [ {"course": "algebra", "score": 20}, {"course": "statistics", "score": 19} ]}'
# json_text = '{"fn":"ali", "last_name":"soltani", "b":"2015-10-21", "bt": 1553717064, "age": 25, "score": {"course": "algebra", "score": 20}}'
# item = Pykson.from_json(json_text, Student)
#
# print(item)
# print(type(item))
#
# print(Pykson.to_json(item))



#
# from pykson import Pykson, JsonObject, IntegerField, StringField, ObjectField


class Score(JsonObject):
    score = IntegerField(serialized_name='s')
    course = StringField(serialized_name='c')
    data = JsonField(serialized_name='d')


class School(JsonObject):
    name = StringField(serialized_name='n')


class Student(JsonObject):

    first_name = StringField(serialized_name="fn")
    last_name = StringField(serialized_name="ln")
    age = IntegerField(serialized_name="a")
    school = ObjectField(School, serialized_name="sc")
    scores = ObjectListField(Score, serialized_name="s")


json_text = '{"fn":"John", "ln":"Smith", "a": 25, "sc": {"n": "MIT"}, "s": [{"s": 100, "c":"Algebra", "d": {"m" :"Metod"}}]}'
student = Pykson.from_json(json_text, Student)
print(Pykson.to_json(student))
a = student.scores[0]
student.school


# class NormalizedOHLCAggregatedIntradayTrade(pykson.JsonObject):
#     SIDE_NONE = 0
#     SIDE_BUY = 1
#     SIDE_SELL = 2
#
#     time_point = pykson.TimestampMillisecondsField(serialized_name='tp')
#     open_price = pykson.FloatField(serialized_name='o')
#     high_price = pykson.FloatField(serialized_name='h')
#     low_price = pykson.FloatField(serialized_name='l')
#     close_price = pykson.FloatField(serialized_name='c')
#     volume = pykson.FloatField(serialized_name='v')
#     trade_count = pykson.IntegerField(serialized_name='tc')
#     sell_trade_volume = pykson.FloatField(serialized_name='stv')
#     sell_trade_count = pykson.IntegerField(serialized_name='stc')
#     buy_trade_volume = pykson.FloatField(serialized_name='btv')
#     buy_trade_count = pykson.IntegerField(serialized_name='btc')
#
#
# class NormalizedOrderBookRow(pykson.JsonObject):
#     ask_count = pykson.IntegerField(serialized_name='ac')
#     ask_price = pykson.FloatField(serialized_name='ap')
#     ask_volume = pykson.FloatField(serialized_name='av')
#     bid_volume = pykson.FloatField(serialized_name='bv')
#     bid_price = pykson.FloatField(serialized_name='bp')
#     bid_count = pykson.IntegerField(serialized_name='bc')
#
#
# class NormalizedOrderBook(pykson.JsonObject):
#     row1 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r1')
#     row2 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r2')
#     row3 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r3')
#     row4 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r4')
#     row5 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r5')
#
#
# class NormalizedIntradayAggregatedData(pykson.JsonObject):
#     time_point = pykson.TimestampMillisecondsField(serialized_name='tp')
#     ohlcv_trade = pykson.ObjectField(NormalizedOHLCAggregatedIntradayTrade, serialized_name='t')
#     order_book = pykson.ObjectField(NormalizedOrderBook, serialized_name='b')
#
#
# class NormalizedDayAggregated(pykson.JsonObject):
#     day = pykson.DateField(serialized_name='d')
#     aggregated_data = pykson.ObjectListField(NormalizedIntradayAggregatedData, serialized_name='ad')
#
# import requests
# resp = requests.get('http://127.0.0.1:8000/crawler/intraday/IRO1BMLT0001/from/2019-03-16/to/2019-03-19/data_points_normalized/5m/')
# resp_data = Pykson.from_json(resp.text, NormalizedDayAggregated)
# print(resp_data)