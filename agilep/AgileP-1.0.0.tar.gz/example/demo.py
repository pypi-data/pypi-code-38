from AgileP.central import Agp
from AgileP.model.extension import SizedString, UnsignedInteger, UnsignedFloat, Email, Bool


class Params(Agp):
    """
    定义数据校验类
    """
    name = SizedString(size=8)
    age = UnsignedInteger(min=100)
    salary = UnsignedFloat(max=10000)
    admin = Bool()
    email = Email()

params = Params("zhang", 100, 9800.1, True, "1234567@qq.com")
print(params.values)
