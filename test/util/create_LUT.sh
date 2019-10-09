sudo python3 syscall_tracer.py &>> tracer_log.txt &
python3 stide_syscall_formatter.py &>> formatter_log.txt &
python3 create_LUT.py &>> LUT_log.txt & 