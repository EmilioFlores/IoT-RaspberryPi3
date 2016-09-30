from pymodbus.client.sync import ModbusTcpClient as ModbusClient


client = ModbusClient("labiotacee.dynalias.org", 505)
if client.connect():
	print client
	result = client.read_holding_registers(303, 1)
	print result.registers
	client.close()
else:
	print "No Connection"
