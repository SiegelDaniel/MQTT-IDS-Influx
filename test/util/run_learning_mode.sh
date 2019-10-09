sudo python3 ./syscall_tracer.py &>> tracer_log.txt &
python3 ./stide_syscall_formatter.py &>> formatter_log.txt &
python3 ./influx_adapter.py &>> influx_adapter_log.txt & 
python3 ./STIDE.py --learn &>> STIDE_log.txt &
python3 ./BoSC.py --learn  &>> BOSC_log.txt & 