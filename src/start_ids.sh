xterm -hold -e 'sudo python3 syscall_tracer.py' &
xterm -hold -e 'python3 stide_syscall_formatter.py' &
xterm -hold -e 'python3 BoSC.py' &
xterm -hold -e 'python3 STIDE.py' &
xterm -hold -e 'python3 influx_adapter.py' &