# cp372-reliable-udp

go-back-n
Terminal 1
Type "cd cp372-reliable-udp"
then
python -m go_back_n sender 5000 5001 4
then

For probabilistic loss:
Terminal 2
Type "cd cp372-reliable-udp"
python -m go_back_n receiver 5001 5000 4 --p 0.2


For deterministic loss:
Terminal 2 
Type "cd cp372-reliable-udp"
python -m go_back_n receiver 5001 5000 4 --d 3
