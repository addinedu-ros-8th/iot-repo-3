enum hard_ware 
{
  rfid
  led_r,
  led_g,
  led_b,
  led_w
}

enum board
{
  User_PC,
  Desk_PC,
  Dynamic,
  Static
}

struct control_data{
  byte function_code,
  byte mode,
  byte led_r,
  byte led_g,
  byte led_b,
  byte led_w,
  byte servo1,
  byte servo2,
  byte linear_actuator_upper,
  byte linear_actuator_lower
}