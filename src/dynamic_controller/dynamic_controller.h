enum hard_ware 
{
  linear_actuator1,
  linear_actuator2,
  servo_motor1,
  servo_motor2
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