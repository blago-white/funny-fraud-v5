from parser.sms.helper import HelperSMSService
from parser.sms.sms365 import SMS365Service

helper = HelperSMSService(apikey="bqFKsHTPW46T1J0TyXJb")
sms365 = SMS365Service(apikey="Uxm9roXN868Qs1Ic4KRoHY4Pzcu9md")

print(helper.get_number())
print(sms365.get_number())
